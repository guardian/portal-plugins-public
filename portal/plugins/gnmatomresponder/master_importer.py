from portal.plugins.kinesisresponder.kinesis_responder import KinesisResponder
import json
import urllib
from django.conf import settings
from s3_mixin import S3Mixin
from vs_mixin import VSMixin
import logging
from gnmvidispine.vs_item import VSItem

from datetime import datetime
import portal.plugins.gnmatomresponder.constants as const

import os
import re
import time

logger = logging.getLogger(__name__)

#Still need: holding image. this is more likely to come from the launch detection side than the atom side.


class MasterImportResponder(KinesisResponder, S3Mixin):
    def get_item_for_atomid(self, atomid):
        """
        Returns a populated VSItem object for the master, or None if no such item exists
        :param atomid:
        :return:
        """
        s = VSItemSearch(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
        s.addCriterion({const.GNM_MASTERS_MEDIAATOM_ATOMID: atomid, const.GNM_TYPE: 'Master'})
        result = s.execute()
        if result.totalItems==0:
            return None
        elif result.totalItems==1:
            return result.results(shouldPopulate=True).next()
        else:
            potential_master_ids = map(lambda item: item.name, result.results(shouldPopulate=False))
            logger.warning("Multiple masters returned for atom ID {0}: {1}. Using the first.".format(atomid, potential_master_ids))
            return potential_master_ids[0]

    @staticmethod
    def get_userid_for_email(email_address):
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(email=email_address)
            logger.info("Got user {0} with id {1} for email {2}".format(user.username, user.pk, email_address))
            return user.pk
        except User.DoesNotExist:
            logger.info("Could not find any user for email {0}".format(email_address))
            return None

    @staticmethod
    def create_placeholder_for_atomid(atomid, title="unknown video", user="unknown_user", parent=None):
        """
        Creates a placeholder and returns a VSItem object for it
        :param atomid: atom ID string
        :param title: title of the new video
        :return: VSItem object
        """
        from gnmvidispine.vs_metadata import VSMetadataReference
        import constants as const
        item = VSItem(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
        project_name_attribs = parent.get_metadata_attributes(const.GNM_PROJECT_HEADLINE)

        reference_list = map(lambda mdref: VSMetadataReference(uuid=mdref.uuid), project_name_attribs[0].values)

        commission_name_attribs = parent.get_metadata_attributes(const.GNM_COMMISSION_TITLE)
        commission_name_ref = commission_name_attribs[0].references

        metadata = {const.GNM_TYPE: 'Master',
                    'title': title,
                    const.GNM_MASTERS_WEBSITE_HEADLINE: title,
                    const.GNM_MASTERS_MEDIAATOM_ATOMID: atomid,
                    const.GNM_MASTERS_GENERIC_TITLEID: atomid,
                    const.GNM_ASSET_CATEGORY: "Master",
                    const.GNM_MASTERS_MEDIAATOM_UPLOADEDBY: user,
                    const.GNM_PROJECT_HEADLINE: reference_list,
                    const.GNM_COMMISSION_TITLE: commission_name_ref
                    }
        userid = MasterImportResponder.get_userid_for_email(user)
        if userid is not None:
            metadata.update({
                const.GNM_MASTERS_GENERIC_OWNER: userid
            })

        item.createPlaceholder(metadata, group='Asset')
        return item

    def get_s3_signed_url(self, bucket=None, key=None):
        """
        Requests a signed URL from S3 to download the given content
        :param bucket:
        :param key:
        :return: String of a presigned URL
        """
        conn = self.get_s3_connection()
        bucketref = conn.get_bucket(bucket)
        keyref = bucketref.get_key(key)
        return keyref.generate_url(DEFAULT_EXPIRY_TIME, query_auth=True)

    @staticmethod
    def get_download_filename(key=None, overridden_name=None):
        safe_basefile = make_filename_re.sub('_', os.path.basename(overridden_name if overridden_name is not None else key))
        deduped_basefile = multiple_underscore_re.sub('_', safe_basefile)

        parts = extract_extension.match(deduped_basefile)
        if parts:
            nameonly = parts.group("basename")
            extension = "." + parts.group("extension")
        else:
            nameonly = deduped_basefile
            extension = ""

        number_part = ""
        n=0
        while True:
            path = os.path.join(settings.ATOM_RESPONDER_DOWNLOAD_PATH, nameonly + number_part + extension)
            if not os.path.exists(path):
                return path
            n+=1
            number_part = "-{0}".format(n)

    def download_to_local_location(self, bucket=None, key=None, filename=None, retries=10, retry_delay=2):
        """
        Downloads the content from the bucket to a location given by the settings
        :param bucket:
        :param key:
        :param filename: file name to download to. If None, then the basename of key is used
        :return: filepath that has been downloaded
        """
        import traceback
        dest_path = self.get_download_filename(key, overridden_name=filename)
        conn = self.get_s3_connection()
        bucketref = conn.get_bucket(bucket)
        keyref = bucketref.get_key(key)

        n=0
        while True:
            logger.info("Downloading {0}/{1} to {2}, attempt {3}...".format(bucket, key, dest_path,n))
            try:
                with open(dest_path, "w") as f:
                    keyref.get_contents_to_file(f)
                logger.info("Done")
                return dest_path
            except Exception as e:
                #if something goes wrong, log it and retry
                logger.error(str(e))
                logger.error(traceback.format_exc())
                time.sleep(retry_delay)
                n+=1
                if n>retries:
                    raise

    def get_collection_for_id(self, projectid):
        """
        Returns a VSCollection for the given project ID. Raises VSNotFound if the collection does not exist, or
        exceptions.NotAProject if it is not a project.
        :return:
        """
        from gnmvidispine.vs_collection import VSCollection
        from .exceptions import NotAProjectError

        collection = VSCollection(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
        collection.populate(projectid)
        if collection.get('gnm_type')!="Project":
            raise NotAProjectError("{0} is a {1}".format(projectid, collection.get('gnm_type')))
        return collection

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

        #TODO: we're going to get two types of message on the stream, one for incoming xml the other for incoming media.
        if content['type'] == const.MESSAGE_TYPE_MEDIA:
            master_item = self.get_item_for_atomid(content['atomId'])
            if master_item is None:
                master_item = self.create_placeholder_for_atomid(content['atomId'],
                                                                 title=content.get('title',None),
                                                                 user=content.get('user', None),
                                                                 parent=project_collection
                                                                 )
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
            logger.info(u"{2}: Download URL for {0} is {1}".format(content['atomId'], download_url, content.get('title','(unknown title)').decode("UTF-8","backslashescape")))
        except UnicodeEncodeError:
            pass

        job_result = master_item.import_to_shape(uri=download_url,
                                                 essence=True,
                                                 shape_tag=getattr(settings,"ATOM_RESPONDER_SHAPE_TAG","lowres"),
                                                 priority=getattr(settings,"ATOM_RESPONDER_IMPORT_PRIORITY","HIGH"),
                                                 jobMetadata={'gnm_source': 'media_atom'},
                                                 )

        try:
            logger.info(u"{n}: Looking for PAC info that has been already registered".format(n=content.get('title','(unknown title)').decode("UTF-8","backslashescape")))
            pac_entry = PacFormXml.objects.get(atom_id=content['atomId'])
            logger.info(u"{n}: Found PAC form information at {0}".format(pac_entry.pacdata_url,n=content.get('title','(unknown title)').decode("UTF-8","backslashescape")))
            proc = PacXmlProcessor(self.role_name, self.session_name)
            proc.link_to_item(pac_entry, master_item)
        except PacFormXml.DoesNotExist:
            logger.info(u"{n}: No PAC form information has yet arrived".format(n=content.get('title','(unknown title)').decode("UTF-8","backslashescape")))

        #make a note of the record. This is to link it up with Vidispine's response message.
        record = ImportJob(item_id=master_item.name,job_id=job_result.name,status='STARTED',started_at=datetime.now(),
                           user_email=content.get('user',"Unknown user"), atom_title=content.get('title', "Unknown title"),
                           s3_path=content['s3Key'])
        record.save()

        parent.addToCollection(master_item)

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
