from celery import shared_task
from celery.decorators import periodic_task
from django.conf import settings
import time
import logging
from datetime import timedelta
import re
logger = logging.getLogger(__name__)


class TranscodeRequested(StandardError):
    def __init__(self, jobid, *args,**kwargs):
        super(TranscodeRequested, self).__init__(*args)
        self.jobid = jobid


class NeedsRetry(StandardError):
    pass


def get_shape_for(itemref, shape_tag, allow_transcode=True):
    """
    Returns a shape reference for the requested shape on the requested item, or
    raises TranscodeRequested if a transcode has been started or raises RuntimeError otherwise
    :param item_id:
    :param shape_tag:
    :return:
    """
    from gnmvidispine.vs_item import VSItem, VSNotFound

    try:
        return itemref.get_shape(shape_tag)
    except VSNotFound:  #shape does not exist on the item
        if allow_transcode:
            jobid = itemref.transcode(shape_tag, priority='MEDIUM', wait=False, allow_object=False)
            raise TranscodeRequested(jobid)
        else:
            raise NeedsRetry()


def s3_connect():
    from boto.s3 import connect_to_region
    #FIXME: need to update these setting names
    if hasattr(settings,'DOWNLOADABLE_LINK_KEY') and hasattr(settings,'DOWNLOADABLE_LINK_SECRET'):
        return connect_to_region(getattr(settings,"AWS_REGION","eu-west-1"),
                                 aws_access_key_id=settings.DOWNLOADABLE_LINK_KEY,
                                 aws_secret_access_key=settings.DOWNLOADABLE_LINK_SECRET
                                 )
    else:
        raise RuntimeError("no credentials")


CHUNK_SIZE=10*1024*1024

def singlepart_upload_vsfile_to_s3(file_ref,filename,mime_type):
    """
    Attempts to add the given file
    :param file_ref: VSFile reference
    :param filename: file name to upload as
    :return: boto.s3.Key for the uploaded file
    """
    import boto.s3.key
    from gnmvidispine.vs_storage import VSFile
    from chunked_downloader import ChunkedDownloader, ChunkDoesNotExist

    if not isinstance(file_ref,VSFile):
        raise TypeError

    download_url = "{u}:{p}/API/storage/file/{id}/data".format(u=settings.VIDISPINE_URL,p=settings.VIDISPINE_PORT,id=file_ref.name)

    d = ChunkedDownloader(download_url, auth=(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD), chunksize=CHUNK_SIZE)

    s3conn = s3_connect()
    bucket = s3conn.get_bucket(settings.DOWNLOADABLE_LINK_BUCKET)
    key = boto.s3.key.Key(bucket)
    key.key = filename

    datastream = d.stream_chunk(0)
    total_size = key.set_contents_from_file(datastream, headers={'Content-Type': mime_type}, reduced_redundancy=True)

    if int(total_size) != int(file_ref.size):
        logger.error("Expected to upload {0} bytes but only uploaded {1}".format(file_ref.size, total_size))
        raise NeedsRetry

    return key


def multipart_upload_vsfile_to_s3(file_ref,filename,mime_type):
    """
    Attempts to add the given file
    :param file_ref: VSFile reference
    :param filename: file name to upload as
    :return: boto.s3.Key for the uploaded file
    """
    from gnmvidispine.vs_storage import VSFile
    import math
    from chunked_downloader import ChunkedDownloader, ChunkDoesNotExist

    if not isinstance(file_ref,VSFile):
        raise TypeError

    download_url = "{u}:{p}/API/storage/file/{id}/data".format(u=settings.VIDISPINE_URL,p=settings.VIDISPINE_PORT,id=file_ref.name)

    expected_parts = int(math.ceil(float(file_ref.size) / float(CHUNK_SIZE)))

    d = ChunkedDownloader(download_url, auth=(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD), chunksize=CHUNK_SIZE)

    s3conn = s3_connect()
    bucket = s3conn.get_bucket(settings.DOWNLOADABLE_LINK_BUCKET)

    #FIXME: check that filename does not exist
    mp = bucket.initiate_multipart_upload(filename,headers={'Content-Type': mime_type}, reduced_redundancy=True)

    def upload_chunk(data_stream, name, part_num):
        for i in range(15):
            try:
                uploaded = mp.upload_part_from_file(data_stream, part_num=part_num+1,)
                logger.info("{0}: uploaded part {1}".format(name, uploaded.__dict__))
                return uploaded
            except Exception as x:
                if i == 10: # retry 10 times
                    raise x
                logger.exception('Failed to upload chunk %s to S3' % part_num)
                time.sleep(1.4 ** i) # exponential back-off

    n=0
    total_size=0

    while True:
        try:
            datastream = d.stream_chunk(n)
            uploaded = upload_chunk(datastream, filename, n)
            total_size+=uploaded.size
            n+=1
        except ChunkDoesNotExist:
            logger.debug("Chunk does not exist, stopping")
            break

    #we should have completed the upload here
    if n<expected_parts:
        logger.error("Expected to upload {0} parts, but apparently completed after {1} parts".format(expected_parts, n))
        mp.cancel_upload()
        raise NeedsRetry
    if int(total_size) != int(file_ref.size):
        logger.error("Expected to upload {0} bytes but only uploaded {1}".format(file_ref.size, total_size))
        mp.cancel_upload()
        raise NeedsRetry
    if n>1:
        #this will give an S3ResponseError: Bad Request if no data was uploaded - https://github.com/boto/boto/issues/3536
        logger.info("{0} completed upload with {1} parts, expected {2}".format(filename, n, expected_parts))
        mp.complete_upload()
    return bucket.get_key(filename)


def upload_vsfile_to_s3(file_ref,filename,mime_type):
    if int(file_ref.size)<CHUNK_SIZE:
        #if we have less than one chunk's worth of data, then upload it all in one go.
        return singlepart_upload_vsfile_to_s3(file_ref,filename,mime_type)
    else:
        return multipart_upload_vsfile_to_s3(file_ref,filename,mime_type)


extension_xtractor = re.compile(r'\.([^\.]+)$')

def get_vsfile_extension(fileref):
    parts = extension_xtractor.search(fileref.uri)
    if parts:
        return parts.group(1)
    else:
        return None


def upload_to_s3(shape_ref,filename):
    from gnmvidispine.vs_shape import VSShape
    if not isinstance(shape_ref, VSShape):
        raise TypeError
    uploaded = False
    s3key = None
    n = 0

    for retry in range(1, int(getattr(settings,'DOWNLOADABLE_LINK_RETRY_LIMIT', 15))):
        logger.info("Upload of any shape for {0}, attempt {1}".format(shape_ref.name, retry))
        for file in shape_ref.files():
            try:
                n+=1
                extension = get_vsfile_extension(file)
                s3key = upload_vsfile_to_s3(file, "{0}.{1}".format(filename, extension),shape_ref.mime_type)
                uploaded = True
                break
            except NeedsRetry:
                logger.warning("Upload of file {0} from shape {1} failed, trying next one".format(file.name, shape_ref.name))
                pass
        if uploaded:
            break
        if n==0:
            #this is caught at the caller, and causes the task to schedule a retry
            raise NeedsRetry("Shape {0} does not yet have any files.".format(shape_ref.name))

    if not uploaded:
        logger.error("No files uploaded")
        raise RuntimeError("No files from shape {0} could upload.".format(shape_ref.name))
    return s3key


def make_filename(string):
    """
    Creates an acceptable filename from the given string
    :param string:
    :return:
    """
    import re
    temp = re.sub(r'[^\w\d]','_', string)
    return re.sub(r'_+','_',temp)


@periodic_task(run_every=timedelta(seconds=getattr(settings,"DOWNLOADABLE_URL_CHECKINTERVAL",30)))
def check_transcode_jobs():
    from models import DownloadableLink
    from gnmvidispine.vs_job import VSJob
    n=0

    for entry in DownloadableLink.objects.filter(status="Transcoding"):
        try:
            n+=1
            j=VSJob(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
            j.populate(entry.transcode_job)
            status = j.status()
            logger.info("Transcode job {0} for {1} of {2} is {3}".format(
                entry.transcode_job, entry.shapetag, entry.item_id, status
            ))
            if j.didFail():
                #if it's failed, then log that fact
                entry.status = "Failed"
                entry.save()
            elif j.finished(noraise=True):
                #if the transcode job is finished, then queue the upload
                entry.status = "Upload Queued"
                entry.save()
                create_link_for.delay(entry.item_id, entry.shapetag)
            else:
                #or just continue to check it
                pass
        except Exception as e:
            logger.error(e)

    return "Checked {0} outstanding transcode jobs".format(n)


def check_transcode_status(job_id):
    """
    Check what the current status of the transcode job is
    :param job_id: job id
    :return: VSJob object
    """
    from gnmvidispine.vs_job import VSJob
    j=VSJob(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
    j.populate(job_id)
    return j

@shared_task
def create_link_for(item_id, shape_tag, obfuscate=True, is_update=False):
    """
    Exception catching wrapper
    :param item_id:
    :param shape_tag:
    :param obfuscate:
    :param is_update:
    :return:
    """
    from models import DownloadableLink
    from traceback import format_exc
    try:
        create_link_for_main(item_id,shape_tag,obfuscate=obfuscate,is_update=is_update)
    except Exception as e:
        try:
            logger.error(e)
            logger.error(format_exc())
            link_model = DownloadableLink.objects.get(item_id=item_id,shapetag=shape_tag)
            link_model.status = 'Failed'
            link_model.save()
            raise
        except DownloadableLink.DoesNotExist:
            pass


def create_link_for_main(item_id, shape_tag, obfuscate=True, is_update=False):
    """
    Task to trigger the optional transcoding and upload of an item
    :param item_id:
    :return:
    """
    from gnmvidispine.vs_item import VSItem
    from uuid import uuid4
    from base64 import b64encode
    from models import DownloadableLink

    link_model = DownloadableLink.objects.get(item_id=item_id,shapetag=shape_tag)
    if link_model.status == "Upload Queued" or link_model.status=="Transcoding":
        allow_transcode = False
    else:
        allow_transcode = True

    if is_update and link_model.status == "Failed":
        raise RuntimeError("Create link failed, requires manual retry")

    item_ref=VSItem(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
    item_ref.populate(item_id, specificFields=['title']) #this will raise VSNotFound if the item_id is invalid

    try:
        shaperef = get_shape_for(item_ref, shape_tag, allow_transcode=allow_transcode)
    except TranscodeRequested as e:
        link_model.status = "Transcoding"
        link_model.transcode_job = e.jobid
        link_model.save()
        create_link_for.apply_async((item_id, shape_tag), kwargs={'obfuscate': obfuscate, 'is_update': True},
                                    countdown=getattr(settings,"DOWNLOADABLE_LINK_RETRYTIME",30))
        return "Transcode requested"
    except NeedsRetry as e:
        #if it's still not present, call ourselves again in up to 30s time.
        create_link_for.apply_async((item_id, shape_tag), kwargs={'obfuscate': obfuscate, 'is_update': True},
                                    countdown=getattr(settings,"DOWNLOADABLE_LINK_RETRYTIME",30))
        return "Still waiting for transcode"

    link_model.status = "Uploading"
    link_model.save()

    if obfuscate:
        filename = make_filename(b64encode(uuid4().get_bytes()))
    else:
        filename = make_filename(item_ref.get('title'))

    try:
        s3key = upload_to_s3(shaperef, filename=filename)
        s3key.set_canned_acl("public-read")
    except NeedsRetry as e:
        #if it's still not present, call ourselves again in up to 30s time.
        create_link_for.apply_async((item_id, shape_tag), kwargs={'obfuscate': obfuscate, 'is_update': True},
                                    countdown=getattr(settings,"DOWNLOADABLE_LINK_RETRYTIME",30))
        return str(e)

    link_model.status = "Available"
    link_model.public_url = s3key.generate_url(expires_in=0, query_auth=False)
    link_model.s3_url = "s3://{0}/{1}".format(settings.DOWNLOADABLE_LINK_BUCKET,s3key.key)

    link_model.save()
    return "Media available at {0}".format(link_model.public_url)


def remove_file_from_s3(s3_url):
    """
    Attempt to delete the given S3 url. This obviously assumes that the credentials for DOWNLOADABLE_LINK in the settings have delete permission.
    AWS exceptions are not caught and should be caught and suitably logged/handled by the caller.
    Additionally, this function will raise a ValueError if the url passed is not in the s3: scheme, or if the requested
    file does not exist in the bucket.
    It will warn if the requested bucket is not the one configured in the settings for DOWNLOADABLE_LINK but will still attempt to delete
    :param s3_url: S3 url to delete
    :return: boto.s3.key.Key object representing the deleted file
    """
    import urlparse
    from urllib import quote, unquote

    broken_down_url = urlparse.urlparse(s3_url)

    logger.info("Attempting to delete {0}".format(s3_url))
    #check url scheme
    if broken_down_url.scheme!="s3":
        raise ValueError("Provided URL is not an S3 URL")

    #s3 urls have the bucket in the "hostname" part and then the path to key

    s3path = unquote(broken_down_url.path)
    if s3path.startswith("/"):
        s3path = s3path[1:] #remove any leading "/" from the filepath

    if s3path=="":
        raise ValueError("No file provided to delete")
    #check bucket name
    if broken_down_url.hostname!=settings.DOWNLOADABLE_LINK_BUCKET:
        logger.warning("Provided bucket {0} does not match expected value from settings {1}".format(broken_down_url.hostname,settings.DOWNLOADABLE_LINK_BUCKET))

    s3conn = s3_connect()
    bucket = s3conn.get_bucket(broken_down_url.hostname)

    key = bucket.get_key(s3path)
    if key is None:
        raise ValueError("File {0} on bucket {1} does not appear to exist".format(s3path, broken_down_url.hostname))
    #exceptions from this are caught in the caller
    key.delete()
    logger.info("Successfully deleted {0}".format(s3_url))
    return key


@periodic_task(run_every=getattr(settings,"DOWNLOADABLE_LINK_CHECK_INTERVAL",300))
def remove_expired_link_files(since=None):
    """
    Regular task to purge out uploaded files that are past their expiry date
    :param since: optional parameter to consider as "now", for testing
    :return: descriptive string
    """
    from models import DownloadableLink
    from datetime import datetime, timedelta
    import traceback

    if since is None:
        since = datetime.now()

    logger.info("Starting remove_expired_link_files")
    total=0
    success=0
    for entry in DownloadableLink.objects.filter(expiry__lte=since):
        total+=1
        try:
            logger.info("Removing {0}".format(str(entry)))
            if entry.status == "Available" or entry.status == "Uploading":
                remove_file_from_s3(entry.s3_url)
            else:
                logger.warning("Removing entry for never completed upload '{0}'".format(str(entry)))
            entry.delete()
            success+=1
        except Exception as e:
            logger.error(traceback.format_exc())
    logger.info("remove_expired_link deleted {0} of {1} files".format(success,total))
    return "Deleted {0} of {1} files".format(success,total)