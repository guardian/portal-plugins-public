from django.conf import settings
from boto import s3, sts
import re
import os
import logging
import time
logger = logging.getLogger(__name__)

make_filename_re = re.compile(r'[^\w\d\.]')
multiple_underscore_re = re.compile(r'_{2,}')
extract_extension = re.compile(r'^(?P<basename>.*)\.(?P<extension>[^\.]+)$')


class S3Mixin(object):
    """
    Mixin class to abstract S3 connections
    """
    def __init__(self, role_name, session_name):
        super(S3Mixin, self).__init__()
        self.role_name = role_name
        self.session_name = session_name

    def get_s3_connection(self):
        """
        Uses temporaray role credentials to connect to S3
        :return:
        """
        sts_conn = sts.connect_to_region('eu-west-1',
                                         aws_access_key_id=getattr(settings,'ATOM_RESPONDER_AWS_KEY_ID',None),
                                         aws_secret_access_key=getattr(settings,'ATOM_RESPONDER_SECRET',None)
                                         )
        credentials = sts_conn.assume_role(self.role_name, self.session_name)
        return s3.connect_to_region('eu-west-1', aws_access_key_id=credentials.credentials.access_key,
                                    aws_secret_access_key=credentials.credentials.secret_key,
                                    security_token=credentials.credentials.session_token)

    default_expiry_time=60

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
        return keyref.generate_url(self.default_expiry_time, query_auth=True)


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
                logger.info("Completed downloading {0}/{1}".format(bucket,key))
                return dest_path
            except Exception as e:
                #if something goes wrong, log it and retry
                logger.error(str(e))
                logger.error(traceback.format_exc())
                time.sleep(retry_delay)
                n+=1
                if n>retries:
                    raise

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