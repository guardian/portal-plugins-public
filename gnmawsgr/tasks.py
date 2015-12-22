import celery
import logging
log = logging.getLogger(__name__)
log.info('Testing logging outside Celery task')

logger = celery.utils.log.get_task_logger(__name__)

@celery.task
def glacier_restore(itemid,path):
    logger.info("Testing logging inside Celery task")
    logger.info("Item is "+itemid)
    logger.info("Path is "+path)
    return 'Finished'



