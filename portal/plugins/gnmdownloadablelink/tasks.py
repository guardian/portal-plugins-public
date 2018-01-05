from celery import shared_task
from celery.decorators import periodic_task
from django.conf import settings
import time
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


class TranscodeRequested(StandardError):
    def __init__(self, jobid, *args,**kwargs):
        super(TranscodeRequested, self).__init__(*args)
        self.jobid = jobid


class NeedsRetry(StandardError):
    pass


def get_shape_for(itemref,shape_tag, allow_transcode=True):
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
        jobid = itemref.transcode(shape_tag, priority='MEDIUM', wait=False, allow_object=False)
        raise TranscodeRequested(jobid)


def s3_connect():
    from boto.s3 import connect_to_region
    return connect_to_region(settings.AWS_REGION,
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                      )


def upload_vsfile_to_s3(file_ref,filename):
    """
    Attempts to add the given file
    :param file_ref: VSFile reference
    :param filename: file name to upload as
    :return: boto.s3.Key for the uploaded file
    """
    from gnmvidispine.vs_storage import VSFile
    import math

    from chunked_downloader import ChunkedDownloader, ChunkDoesNotExist
    from chunked_downloader import DEFAULT_CHUNKSIZE as CHUNK_SIZE

    if not isinstance(file_ref,VSFile):
        raise TypeError

    download_url = "{u}:{p}/API/storage/file/{id}/data".format(u=settings.VIDISPINE_URL,p=settings.VIDISPINE_PORT,id=file_ref.name)

    expected_parts = int(math.ceil(file_ref.size / float(CHUNK_SIZE)))

    d = ChunkedDownloader(download_url, auth=(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD))

    s3conn = s3_connect()
    bucket = s3conn.get_bucket(settings.DOWNLOADABLE_LINK_BUCKET)
    key = bucket.get_key(filename)
    #FIXME: check that filename does not exist
    mp = bucket.initiate_multipart_upload(filename)

    def upload_chunk(data_stream, name, part_num):
        for i in range(15):
            try:
                uploaded = mp.upload_part_from_file(data_stream, part_num=part_num,)
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
            datastream = d.get_chunk(n)
            uploaded = upload_chunk(datastream, filename, n)
            total_size+=uploaded.size
            n+=1
        except ChunkDoesNotExist:
            break

    #we should have completed the upload here
    if n<expected_parts:
        logger.error("Expected to upload {0} parts, but apparently completed after {1} parts".format(expected_parts, n))
        mp.cancel_upload()
        raise NeedsRetry
    if total_size<file_ref.size:
        logger.error("Expected to upload {0} bytes but only uploaded {1}".format(file_ref.size, total_size))
        mp.cancel_upload()
        raise NeedsRetry
    if n>1:
        #this will give an S3ResponseError: Bad Request if no data was uploaded - https://github.com/boto/boto/issues/3536
        logger.info("{0} completed upload with {1} parts, expected {2}".format(filename, n, expected_parts))
        mp.complete_upload()
    return bucket.get_key(filename)


def upload_to_s3(shape_ref,filename):
    from gnmvidispine.vs_shape import VSShape
    if not isinstance(shape_ref, VSShape):
        raise TypeError
    uploaded = False
    s3key = None

    for file in shape_ref.files():
        try:
            s3key = upload_vsfile_to_s3(file, filename)
            uploaded = True
            break
        except NeedsRetry:
            logger.warning("Upload of file {0} from shape {1} failed, trying next one".format(file.name, shape_ref.name))
            pass

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


@periodic_task(run_every=timedelta(seconds=getattr(settings,"DOWNLOADABLE_URL_CHECKINTERVAL",5)))
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
            if status=="FINISHED":
                #if the transcode job is finished, then queue the upload
                entry.status = "Upload Queued"
                entry.save()
                create_link_for.delay(entry.item_id, entry.shapetag)
            elif status=="FAILED":
                #if it's failed, then log that fact
                entry.status = "Failed"
                entry.save()
            else:
                #or just continue to check it
                pass
        except Exception as e:
            logger.error(e)

    return "Checked {0} outstanding transcode jobs".format(n)


@shared_task
def create_link_for(item_id, shape_tag, obfuscate=True):
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

    item_ref=VSItem(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
    item_ref.populate(item_id, specificFields=['title'])

    try:
        shaperef = get_shape_for(item_ref, shape_tag, allow_transcode=allow_transcode)
    except TranscodeRequested as e:
        link_model.status = "Transcoding"
        link_model.transcode_job = e.jobid
        link_model.save()
        return "Transcode requested"

    link_model.status = "Uploading"
    link_model.save()

    if obfuscate:
        filename = make_filename(b64encode(uuid4().get_bytes()))
    else:
        filename = make_filename(item_ref.get('title'))

    s3key = upload_to_s3(shaperef, filename=filename)
    s3key.set_acl("ACL_PUBLIC") #CHECK this is the right call
    link_model.status = "Available"
    link_model.public_url = s3key.get_url() #CHECK this is the right call
    link_model.s3_url = "s3://{0}/{1}".format(settings.DOWNLOADABLE_LINK_BUCKET,s3key.key)
    link_model.save()
    return "Media available at {0}".format(link_model.public_url)