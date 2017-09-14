from portal.plugins.kinesisresponder.kinesis_responder import KinesisResponder
import json
from pprint import pprint
from urlparse import urlparse
import os.path
from django.conf import settings
from boto import sts, s3
import logging
from gnmvidispine.vs_item import VSItem
from gnmvidispine.vs_collection import VSCollection
from gnmvidispine.vs_search import VSItemSearch
from datetime import datetime
import portal.plugins.gnmatomresponder.constants as const
from portal.plugins.gnmatomresponder.exceptions import NotAProjectError

logger = logging.getLogger(__name__)

#Still need: video title, holding image

DEFAULT_EXPIRY_TIME=3600

class MasterImportResponder(KinesisResponder):
    def get_s3_connection(self):
        """
        Uses temporaray role credentials to connect to S3
        :return:
        """
        sts_conn = sts.connect_to_region('eu-west-1')
        credentials = sts_conn.assume_role(self.role_name, self.session_name)
        return s3.connect_to_region('eu-west-1', aws_access_key_id=credentials.credentials.access_key,
                                               aws_secret_access_key=credentials.credentials.secret_key,
                                               security_token=credentials.credentials.session_token)

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

    def create_placeholder_for_atomid(self, atomid, title="unknown video"):
        """
        Creates a placeholder and returns a VSItem object for it
        :param atomid: atom ID string
        :param title: title of the new video
        :return: VSItem object
        """
        item = VSItem(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
        item.createPlaceholder({const.GNM_TYPE: 'Master',
                                'title': title,
                                const.GNM_MASTERS_WEBSITE_HEADLINE: title
                                const.GNM_MASTERS_MEDIAATOM_ATOMID: atomid
                                }, group='Asset')
        return item

    def get_s3_signed_url(self, bucket=None, key=None):
        """
        Requests a signed URL from S3 to download the given content
        :param bucket:
        :param key:
        :return:
        """
        conn = self.get_s3_connection()
        bucket = conn.get_bucket(bucket)
        key = bucket.get_key(key)
        return key.generate_url(DEFAULT_EXPIRY_TIME, query_auth=True)

    def get_collection_for_id(self, projectid):
        """
        Returns a VSCollection for the given project ID. Raises VSNotFound if the collection does not exist, or
        exceptions.NotAProject if it is not a project.
        :return:
        """
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
        from models import ImportJob
        content = json.loads(record)

        master_item = self.get_item_for_atomid(content['atomId'])
        if master_item is None:
            master_item = self.create_placeholder_for_atomid(content['atomId'], title="unknown video")

        if not isinstance(master_item, VSItem): raise TypeError #for intellij

        download_url = self.get_s3_signed_url(bucket=settings.ATOM_RESPONDER_DOWNLOAD_BUCKET, key=content['s3Key'])
        logger.info("Download URL for {0} is {1}".format(content['atomId'], download_url))

        job_result = master_item.import_to_shape(uri=download_url,
                                                 essence=True,
                                                 shape_tag='original',
                                                 priority=getattr(settings,"ATOM_RESPONDER_IMPORT_PRIORITY","HIGH"),
                                                 job_metadata={'gnm_source': 'media_atom'})

        #make a note of the record. This is to link it up with Vidispine's response message.
        record = ImportJob(item_id=master_item.name,job_id=job_result.name,status='STARTED',started_at=datetime.now())
        record.save()

        project_collection = self.get_collection_for_id(content['projectId'])
        if project_collection is None:
            project_collection = getattr(settings,'ATOM_RESPONDER_DEFAULT_PROJECTID',None)
            if project_collection is None:
                raise RuntimeError("Unable to get a project ID for master {0}, and no default is set".format(master_item.name))
        project_collection.addToCollection(master_item)
