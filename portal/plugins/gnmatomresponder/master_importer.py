from portal.plugins.kinesisresponder.kinesis_responder import KinesisResponder
import json
from pprint import pprint
from urlparse import urlparse
import os.path
from django.conf import settings
from boto import s3
import logging
from gnmvidispine.vs_item import VSItem
from gnmvidispine.vs_job import VSJob
from time import sleep
from datetime import datetime

logger = logging.getLogger(__name__)

#Still need: video title


class MasterImportResponder(KinesisResponder):
    def get_item_for_atomid(self, atomid):
        """
        Returns a populated VSItem object for the master, or None if no such item exists
        :param atomid:
        :return:
        """

    def create_placeholder_for_atomid(self, atomid, title="unknown video"):
        """
        Creates a placeholder and returns a VSItem object for it
        :param atomid:
        :param title:
        :return:
        """

    def get_s3_signed_url(self, bucket=None, key=None):
        """
        Requests a signed URL from S3 to download the given content
        :param bucket:
        :param key:
        :return:
        """

    def process(self,record, approx_arrival):
        from models import ImportJob
        content = json.loads(record)

        master_item = self.get_item_for_atomid(content['atomId'])
        if master_item is None:
            master_item = self.create_placeholder_for_atomid(content['atomId'], title="unknown video")

        if not isinstance(master_item, VSItem): raise TypeError #for intellij

        download_url = self.get_s3_signed_url(bucket=settings.ATOM_RESPONDER_DOWNLOAD_BUCKET, key=content['s3Key'])

        job_result = master_item.import_to_shape(uri=download_url,
                                                 essence=True,
                                                 shape_tag='original',
                                                 priority=getattr(settings,"ATOM_RESPONDER_IMPORT_PRIORITY","HIGH"),
                                                 job_metadata={'gnm_source': 'media_atom'})

        #make a note of the record. This is to link it up with Vidispine's response message.
        record = ImportJob(item_id=master_item.name,job_id=job_result.name,status='STARTED',started_at=datetime.now())

        # if not isinstance(job_result,VSJob): raise TypeError #for intellij
        # while not job_result.finished(noraise=False): #an exception is raised if the import fails
        #     logger.info("Import of {uri} to {itemid} is {status}".format(
        #         uri = download_url,
        #         itemid = master_item.name,
        #         status=job_result.status()
        #     ))
        #     sleep(10)
        #     job_result.update()