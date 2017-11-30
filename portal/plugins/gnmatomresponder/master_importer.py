from portal.plugins.kinesisresponder.kinesis_responder import KinesisResponder
import json
import urllib
from django.conf import settings
from s3_mixin import S3Mixin
from vs_mixin import VSMixin
import logging
from gnmvidispine.vs_item import VSItem
from gnmvidispine.vs_search import VSItemSearch
from datetime import datetime
import portal.plugins.gnmatomresponder.constants as const

import os
import re
import time

logger = logging.getLogger(__name__)

#Still need: holding image. this is more likely to come from the launch detection side than the atom side.

extract_extension = re.compile(r'^(?P<basename>.*)\.(?P<extension>[^\.]+)$')
multiple_underscore_re = re.compile(r'_{2,}')
make_filename_re = re.compile(r'[^\w\d\.]')


class MasterImportResponder(KinesisResponder, S3Mixin, VSMixin):
    def process(self,record, approx_arrival):
        """
        Process a message from the kinesis stream.  Each record is a JSON document which contains keys for atomId, s3Key,
        projectId.  This will find an item with the given atom ID or create a new one, get a signed download URL from
        S3 for the media and then instruct Vidsipine to import it.
        Rather than wait for the job to complete here, we return immediately and rely on receiving a message from VS
        when the job terminates.
        :param record: JSON document in the form of a string
        :param approx_arrival:
        :return:
        """
        content = json.loads(record)

        logger.info(content)

        project_collection = self.get_collection_for_id(content['projectId'])
        if project_collection is None:
            project_collection = getattr(settings,'ATOM_RESPONDER_DEFAULT_PROJECTID',None)
            if project_collection is None:
                raise RuntimeError("Unable to get a project ID for atom {0}, and no default is set".format(content['atomId']))

        #We get two types of message on the stream, one for incoming xml the other for incoming media.
        if content['type'] == const.MESSAGE_TYPE_MEDIA:
            master_item = self.get_item_for_atomid(content['atomId'])
            if master_item is None:
                master_item = self.create_placeholder_for_atomid(content['atomId'],
                                                                 title=content.get('title',None),
                                                                 user=content.get('user', None),
                                                                 parent=project_collection
                                                                 )
                logger.info("Created item {0} for atom {1}".format(master_item.name, content['atomId']))
            return self.import_new_item(master_item, content)
        elif content['type'] == const.MESSAGE_TYPE_PAC:
            record = self.register_pac_xml(content)
            self.ingest_pac_xml(record)
        else:
            raise ValueError("Unrecognised message type: {0}".format(content['type']))

    def register_pac_xml(self, content):
        """
        Start the import of new PAC data by registering it in the database.
        :param content: JSON message content as received from atom tool
        :return: the database model instance
        """
        from models import PacFormXml

        (record, created) = PacFormXml.objects.get_or_create(atom_id=content['atomId'], defaults={'received': datetime.now()})
        if not created:
            logger.info("PAC form xml had already been delivered for {0}, over-writing".format(content['atomId']))

        record.completed = None
        record.status = "UNPROCESSED"
        record.last_error = ""
        record.pacdata_url = "s3://{bucket}/{path}".format(bucket=content['s3Bucket'], path=content['s3Path'])
        record.save()
        return record

    def import_new_item(self, master_item, content, parent=None):
        from models import ImportJob, PacFormXml
        from pac_xml import PacXmlProcessor
        from mock import MagicMock
        if not isinstance(master_item, VSItem) and not isinstance(master_item, MagicMock): raise TypeError #for intellij
        #using a signed URL is preferred, but right now VS seems to have trouble ingesting it.
        #so, we download instead and ingest that. get_s3_signed_url is left in to make it simple to switch back
        #download_url = self.get_s3_signed_url(bucket=settings.ATOM_RESPONDER_DOWNLOAD_BUCKET, key=content['s3Key'])
        downloaded_path = self.download_to_local_location(bucket=settings.ATOM_RESPONDER_DOWNLOAD_BUCKET,
                                                          key=content['s3Key'],
                                                          #this is converted to a safe filename within download_to_local_location
                                                          filename=content.get('title', None)) #filename=None => use s3key instead

        download_url = "file://" + urllib.quote(downloaded_path)

        try:
            logger.info(u"{2}: Download URL for {0} is {1}".format(content['atomId'], download_url, content.get('title','(unknown title)').encode("UTF-8","backslashescape")))
        except UnicodeEncodeError:
            pass
        except UnicodeDecodeError:
            pass

        job_result = master_item.import_to_shape(uri=download_url,
                                                 essence=True,
                                                 shape_tag=getattr(settings,"ATOM_RESPONDER_SHAPE_TAG","lowres"),
                                                 priority=getattr(settings,"ATOM_RESPONDER_IMPORT_PRIORITY","HIGH"),
                                                 jobMetadata={'gnm_source': 'media_atom'},
                                                 )
        logger.info(u"{0} Import job is at ID {1}".format(content['atomId'], job_result.name))

        try:
            logger.info(u"{n}: Looking for PAC info that has been already registered".format(n=content.get('title','(unknown title)').encode("UTF-8","backslashescape")))
            pac_entry = PacFormXml.objects.get(atom_id=content['atomId'])
            logger.info(u"{n}: Found PAC form information at {0}".format(pac_entry.pacdata_url,n=content.get('title','(unknown title)').encode("UTF-8","backslashescape")))
            proc = PacXmlProcessor(self.role_name, self.session_name)
            proc.link_to_item(pac_entry, master_item)
        except PacFormXml.DoesNotExist:
            logger.info(u"{n}: No PAC form information has yet arrived".format(n=content.get('title','(unknown title)').encode("UTF-8","backslashescape")))

        #make a note of the record. This is to link it up with Vidispine's response message.
        record = ImportJob(item_id=master_item.name,job_id=job_result.name,status='STARTED',started_at=datetime.now(),
                           user_email=content.get('user',"Unknown user"), atom_title=content.get('title', "Unknown title"),
                           s3_path=content['s3Key'])
        record.save()

        logger.info(u"{0}: Adding item {1} to collection {2}".format(content['atomId'], master_item.name, parent.name))
        parent.addToCollection(master_item)
        logger.info(u"{0}: Done".format(content['atomId']))
        
    def ingest_pac_xml(self, pac_xml_record):
        """
        Master process to perform import of pac data
        :param pac_xml_record: instance of PacFormXml model
        :return:
        """
        from pac_xml import PacXmlProcessor

        vsitem = self.get_item_for_atomid(pac_xml_record.atom_id)
        if vsitem is None:
            logger.warning("No item could be found for atom ID {0}, waiting for it to arrive".format(pac_xml_record.atom_id))
            return

        proc = PacXmlProcessor(self.role_name,self.session_name)

        #this process will call out to Pluto to do the linkup once the data has been received
        return proc.link_to_item(pac_xml_record, vsitem)