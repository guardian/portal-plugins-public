import celery
from celery.decorators import periodic_task
from celery import shared_task
from celery.schedules import crontab
from datetime import datetime, timedelta
import logging
from django.db.models import Q
from django.conf import settings
import traceback

logger = logging.getLogger(__name__)


@periodic_task(run_every=crontab(minute=23,hour=23))
def cleanup_old_importjobs():
    """
    Scheduled task to remove all finished entries older than 30 days from the database
    :return:
    """
    from models import ImportJob
    from portal.plugins.kinesisresponder.sentry import inform_sentry_exception
    try:
        qs = ImportJob.objects\
            .filter(Q(status='FINISHED') | Q(status='FINISHED_WARNING'))\
            .filter(completed_at__lte=datetime.now()-timedelta(days=30))

        logger.info("Cleaning out {0} import jobs".format(qs.count()))
        qs.delete()
        logger.info("Done")
    except Exception:
        logger.error(traceback.format_exc())
        inform_sentry_exception()


def delete_from_s3(conn, record):
    """
    Deletes the raw media from the specified ImportJob record from S3
    :param conn: Boto s3 connection object
    :param record: ImportJob record
    :return: Boolean
    """
    from models import ImportJob
    from portal.plugins.kinesisresponder.sentry import inform_sentry_exception

    if not isinstance(record, ImportJob): raise TypeError
    if record.s3_path is None:
        return True

    bucket = conn.get_bucket(settings.ATOM_RESPONDER_DOWNLOAD_BUCKET)
    try:
        bucket.delete_key(record.s3_path)
        record.s3_path = None
        record.save()
        return True
    except Exception as e:
        #don't break the loop if it fails
        logger.error("Unable to delete {0} from record {1}: {2}".format(record.s3_path, str(record), str(e)))
        logger.error(traceback.format_exc())
        inform_sentry_exception({
            "record": record.__dict__
        })
        return False


# @periodic_task(run_every=crontab(minute=31))
# def cleanup_s3_files():
#     """
#     Scheduled task to delete the original media for successfully imported jobs
#     :return:
#     """
#     from models import ImportJob
#     from master_importer import S3Mixin
#     s3_connector = S3Mixin(settings.ATOM_RESPONDER_ROLE_NAME, "AutoDeleteSession")
#
#     qs = ImportJob.objects\
#         .filter(Q(status='FINISHED') | Q(status='FINISHED_WARNING'))\
#         .filter(completed_at__lte=datetime.now()-timedelta(days=1))
#
#     conn = s3_connector.get_s3_connection()
#     logger.info("Removing {0} job files from s3 bucket".format(qs.count()))
#     results = map(lambda record: delete_from_s3(conn, record), qs)
#
#     succeeded = len(filter(lambda result: result, results))
#     failed = len(filter(lambda result: not result, results))
#     logger.info("Cleanup completed, removed {0} files, {1} failed".format(succeeded, failed))


@periodic_task(run_every=crontab(minute=45))
def check_unprocessed_pacxml():
    """
    Scheduled task to check if any unprocessed pac forms have "fallen through the cracks"
    :return:
    """
    from models import PacFormXml
    from pac_xml import PacXmlProcessor
    from django.conf import settings
    from vs_mixin import VSMixin

    role_name = settings.ATOM_RESPONDER_ROLE_NAME
    session_name = "GNMAtomResponderTimed"

    vs = VSMixin()
    proc = PacXmlProcessor(role_name,session_name)

    queryset = PacFormXml.objects.filter(status="UNPROCESSED")

    logger.info("check_unprocessed_pacxml: Found {0} unprocessed records".format(queryset.count()))

    for pac_xml_record in queryset:
        vsitem = vs.get_item_for_atomid(pac_xml_record.atom_id)
        #this process will call out to Pluto to do the linkup once the data has been received
        if vsitem is not None:
            logger.info("check_unprocessed_pacxml: Found item {0} for atom {1}".format(vsitem.name, pac_xml_record.atom_id))
            proc.link_to_item(pac_xml_record, vsitem)
            logger.info("check_unprocessed_pacxml: linkup initiated for {0} from {1}".format(vsitem.name, pac_xml_record.atom_id))
        else:
            logger.info("check_unprocessed_pacxml: No items found for atom {0}".format(pac_xml_record.atom_id))

    logger.info("check_unprocessed_pacxml: run completed")


def delete_s3_url(conn, s3_url):
    from urlparse import urlparse

    parsed = urlparse(s3_url)
    if parsed.scheme != "s3":
        raise ValueError("delete_s3_url called on something not an s3 url (was {0})".format(parsed.scheme))

    bucket = conn.get_bucket(parsed.hostname)
    if parsed.path.startswith('/'):
        path = parsed.path[1:]
    else:
        path = parsed.path

    bucket.delete_key(path)


@periodic_task(run_every=crontab(minute=55))
def expire_processed_pacrecords():
    """
    Scheduled task to remove pac xml records for items that have been processed
    :return:
    """

    from models import PacFormXml
    from django.conf import settings
    from master_importer import S3Mixin

    queryset = PacFormXml.objects.filter(status="PROCESSED",completed__lte=datetime.now()-timedelta(days=1))

    logger.info("expire_processed_pacrecords: found {0} records processed and older than 1 day to purge".format(queryset.count()))
    s3_connector = S3Mixin(settings.ATOM_RESPONDER_ROLE_NAME, "AutoDeletePacSession")

    conn = s3_connector.get_s3_connection()

    for pac_record in queryset:
        logger.info("expire_processed_pacrecords: purging record for atom {0}".format(pac_record.atom_id))
        delete_s3_url(conn, pac_record.pacdata_url)
        pac_record.delete()
    logger.info("expire_processed_pacrecords completed")


@shared_task
def timed_request_resend(atom_id):
    """
    task that can run after a delay to request that an item is resent
    :param atom_id:  atom id to resend
    :return:
    """
    from media_atom import request_atom_resend
    from portal.plugins.kinesisresponder.sentry import inform_sentry_exception

    try:
        logger.info("Requesting resend of atom {0}".format(atom_id))
        request_atom_resend(atom_id, settings.ATOM_TOOL_HOST, settings.ATOM_TOOL_SECRET)
        logger.info("Resend of atom {0} done".format(atom_id))
        #logger.error("timed_request_resend is currently disabled.")
    except Exception as e:
        logger.error(e)
        inform_sentry_exception()
        raise


@shared_task
def timed_retry_process_message(record, approx_arrival, attempt=0):
    """
    task that can be used to retry an ingest if messages have arrived before content is available
    :return:
    """
    from master_importer import MasterImportResponder
    from management.commands.run_atom_responder import Command as AtomResponderCommand
    import json

    content = json.loads(record)
    logger.info("{0}: starting timed retry".format(content['atomId']))
    imp = MasterImportResponder(AtomResponderCommand.role_name, AtomResponderCommand.session_name,
                                AtomResponderCommand.stream_name, "timed-resync",
                                aws_access_key_id=settings.ATOM_RESPONDER_AWS_KEY_ID,
                                aws_secret_access_key=settings.ATOM_RESPONDER_SECRET)

    imp.process(record, approx_arrival, attempt=attempt)
    logger.info("{0}: timed retry completed".format(content['atomId']))