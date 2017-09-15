import celery
from datetime import datetime, timedelta
import logging
from django.db.models import Q

logger = logging.getLogger(__name__)


@celery.task
def cleanup_old_importjobs():
    from models import ImportJob

    qs = ImportJob.objects\
        .filter(Q(status='FINISHED') | Q(status='FINISHED_WARNING'))\
        .filter(completed_at__gte=datetime.now()-timedelta(days=60))

    logger.info("Cleaning out {0} import jobs".format(qs.count()))
    qs.delete()
    logger.info("Done")