from portal.plugins.kinesisresponder.kinesis_responder import KinesisResponder
import json
import urllib
from django.conf import settings
from s3_mixin import S3Mixin, FileDoesNotExist
from vs_mixin import VSMixin
import logging
from gnmvidispine.vs_item import VSItem, VSNotFound
from datetime import datetime
import portal.plugins.gnmatomresponder.constants as const
import re

logger = logging.getLogger(__name__)

#Still need: holding image. this is more likely to come from the launch detection side than the atom side.

extract_extension = re.compile(r'^(?P<basename>.*)\.(?P<extension>[^\.]+)$')
multiple_underscore_re = re.compile(r'_{2,}')
make_filename_re = re.compile(r'[^\w\d\.]')


class MasterImportResponder(KinesisResponder, S3Mixin, VSMixin):
    def get_project_collection(self, content):
        """
        Gets a populated VSCollection reference to the project collection mentioned in content
        :param content: parsed json message including the 'projectId' key
        :return:
        """
        from .exceptions import NotAProjectError

        try:
            project_collection = self.get_collection_for_id(content['projectId'])
        except VSNotFound:
            try:
                logger.warning(u"Invalid parent collection {0} specified for atom {1} ({2}). Falling back to default.".format(
                    content['projectId'], content['atomId'],
                    content.get('title','(unknown title)').encode("UTF-8","backslashescape")
                ))
            except UnicodeDecodeError:
                pass
            except UnicodeEncodeError:
                pass
            project_collection = None
        except NotAProjectError:
            try:
                logger.warning(u"Collection {0} specified for atom {1} ({2}) is not a Project. Falling back to default.".format(
                    content['projectId'], content['atomId'],
                    content.get('title','(unknown title)').encode("UTF-8","backslashescape")
                ))
            except UnicodeDecodeError:
                pass
            except UnicodeEncodeError:
                pass
            project_collection = None

        if project_collection is None:
            collection_id = getattr(settings,'ATOM_RESPONDER_DEFAULT_PROJECTID',None)
            if collection_id is None:
                raise RuntimeError("Unable to get a project ID for atom {0}, and no default is set".format(content['atomId']))
            else:
                project_collection = self.get_collection_for_id(collection_id)

        return project_collection

    def update_pluto_record(self, item_id):
        import traceback
        try:
            from portal.plugins.gnm_masters.signals import master_external_update

            master_external_update.send(sender=self.__class__, item_id=item_id)
        except ImportError as e:
            logger.error("Unable to signal master update: {0}".format(e))
        except Exception as e:
            logger.error("An error happened when outputting master_external_create signal: {0}".format(traceback.format_exc()))

    def get_or_create_master_item(self, atomId, title, project_collection, user):
        master_item = self.get_item_for_atomid(atomId)

        created = False

        if master_item is None:
            if title is None:
                raise RuntimeError("Title field not set for atom {0}.".format(atomId))
            if user is None:
                logger.warning("User field not set for atom {0}.".format(atomId))
                user_to_set="unknown_user"
            else:
                user_to_set=user
            master_item = self.create_placeholder_for_atomid(atomId,
                                                             title=title,
                                                             user=user_to_set,
                                                             parent=project_collection
                                                             )
            logger.info("Created item {0} for atom {1}".format(master_item.name, atomId))
            created = True
        return master_item, created

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
        from media_atom import request_atom_resend
        content = json.loads(record)

        logger.info(content)

        #We get two types of message on the stream, one for incoming xml the other for incoming media.
        if content['type'] == const.MESSAGE_TYPE_MEDIA or content['type'] == const.MESSAGE_TYPE_RESYNC_MEDIA:
            project_collection = self.get_project_collection(content)
            if 'user' in content:
                atom_user = content['user']
            else:
                atom_user = None
            master_item, created = self.get_or_create_master_item(content['atomId'], content['title'], project_collection, atom_user)

            return self.import_new_item(master_item, content, parent=project_collection)
        elif content['type'] == const.MESSAGE_TYPE_PAC:
            logger.info("Got PAC form data message")
            record = self.register_pac_xml(content)
            self.ingest_pac_xml(record)
            logger.info("PAC form data message complete")
        elif content['type'] == const.MESSAGE_TYPE_PROJECT_ASSIGNED:
            logger.info("Got project (re-)assignment message: {0}".format(content))
            # project_collection = self.get_project_collection(content)
            # if 'title' in content:
            #     atom_title = content['title']
            # else:
            #     atom_title = None
            # if 'user' in content:
            #     atom_user = content['user']
            # else:
            #     atom_user = None

            master_item = self.get_item_for_atomid(content['atomId'])
            if master_item is not None:
                logger.info("Master item for atom already exists at {0}, assigning".format(master_item.name))
                self.assign_atom_to_project(content['atomId'], content['commissionId'], content['projectId'], master_item)
            else:
                logger.warning("No master item exists for atom {0}.  Requesting a re-send from media atom tool".format(content['atomId']))
                request_atom_resend(content['atomId'], settings.ATOM_TOOL_HOST, settings.ATOM_TOOL_SECRET)
            logger.info("Project (re-)assignment complete")
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

        safe_title = content.get('title','(unknown title)').encode("UTF-8","backslashescape").decode("UTF-8")

        #using a signed URL is preferred, but right now VS seems to have trouble ingesting it.
        #so, we download instead and ingest that. get_s3_signed_url is left in to make it simple to switch back
        #download_url = self.get_s3_signed_url(bucket=settings.ATOM_RESPONDER_DOWNLOAD_BUCKET, key=content['s3Key'])
        downloaded_path = self.download_to_local_location(bucket=settings.ATOM_RESPONDER_DOWNLOAD_BUCKET,
                                                          key=content['s3Key'],
                                                          #this is converted to a safe filename within download_to_local_location
                                                          filename=content.get('title', None)) #filename=None => use s3key instead

        download_url = "file://" + urllib.quote(downloaded_path)

        logger.info(u"{n}: Ingesting atom with title '{0}' from media atom with ID {1}".format(safe_title, content['atomId'], n=master_item.name))
        try:
            logger.info(u"{n}: Download URL is {0}".format(download_url, n=master_item.name))
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
        logger.info(u"{0} Import job is at ID {1}".format(master_item.name, job_result.name))

        master_item.set_metadata({const.GNM_ASSET_FILENAME: downloaded_path})

        self.update_pluto_record(master_item.name)
        #make a note of the record. This is to link it up with Vidispine's response message.
        record = ImportJob(item_id=master_item.name,
                           job_id=job_result.name,
                           status='STARTED',
                           started_at=datetime.now(),
                           user_email=content.get('user',"Unknown user"),
                           atom_id=content['atomId'],
                           atom_title=content.get('title', "Unknown title"),
                           s3_path=content['s3Key'])
        previous_attempt = record.previous_attempt()
        if previous_attempt:
            record.retry_number = previous_attempt.retry_number+1
            logger.info(u"{0} Import job is retry number {1}".format(master_item.name, record.retry_number))
        record.save()

        try:
            logger.info(u"{n}: Looking for PAC info that has been already registered".format(n=master_item.name))
            pac_entry = PacFormXml.objects.get(atom_id=content['atomId'])
            logger.info(u"{n}: Found PAC form information at {0}".format(pac_entry.pacdata_url,n=master_item.name))
            proc = PacXmlProcessor(self.role_name, self.session_name)
            proc.link_to_item(pac_entry, master_item)
        except PacFormXml.DoesNotExist:
            logger.info(u"{n}: No PAC form information has yet arrived".format(n=master_item.name))

        if parent is not None:
            logger.info(u"{0}: Adding to collection {1}".format(master_item.name, parent.name))
            parent.addToCollection(master_item)
            logger.info(u"{0}: Done".format(master_item.name))
        else:
            logger.error(u"{0}: No parent collection specified for item!".format(master_item.name))
        
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

    def assign_atom_to_project(self, atomId, commissionId, projectId, master_item):
        """
        (re)-assigns the given master to a project.
        If the project is not associated with the given commission, warns but does not fail.
        :param atomId:
        :param commissionId:
        :param projectId:
        :return:
        """

        current_project_id = master_item.get(const.PARENT_COLLECTION)
        if current_project_id is not None:
            logger.warning("Re-assigning master {0} to project {1} so removing from {2}".format(master_item.name, projectId, current_project_id))
            current_project_ref = self.get_collection_for_id(current_project_id)
            current_project_ref.removeFromCollection(master_item)

        new_project_ref = self.get_collection_for_id(projectId)
        expected_commission_id = new_project_ref.get(const.PARENT_COLLECTION)
        if expected_commission_id!=commissionId:
            logger.warning("Project {0} belongs to commission {1}, but media atom thinks it belongs to commission {2}. Continuing anyway".format(projectId, expected_commission_id, commissionId))

        logger.info("Adding master {0} to collection {1}".format(master_item.name, new_project_ref.name))
        new_project_ref.addToCollection(master_item)
        logger.info("Setting up project fields for {0}".format(master_item.name))
        self.set_project_fields_for_master(master_item,parent_project=new_project_ref)
        logger.info("Telling gnm_masters about updates for {0}".format(master_item.name))
        self.update_pluto_record(master_item.name)