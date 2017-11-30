import celery
from celery.decorators import periodic_task
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


@periodic_task(run_every=crontab(minute=31))
def cleanup_s3_files():
    """
    Scheduled task to delete the original media for successfully imported jobs
    :return:
    """
    from models import ImportJob
    from master_importer import S3Mixin
    s3_connector = S3Mixin(settings.ATOM_RESPONDER_ROLE_NAME, "AutoDeleteSession")

    qs = ImportJob.objects\
        .filter(Q(status='FINISHED') | Q(status='FINISHED_WARNING'))\
        .filter(completed_at__gte=datetime.now()-timedelta(days=1))

    conn = s3_connector.get_s3_connection()
    logger.info("Removing {0} job files from s3 bucket".format(qs.count()))
    results = map(lambda record: delete_from_s3(conn, record), qs)

    succeeded = len(filter(lambda result: result, results))
    failed = len(filter(lambda result: not result, results))
    logger.info("Cleanup completed, removed {0} files, {1} failed".format(succeeded, failed))
