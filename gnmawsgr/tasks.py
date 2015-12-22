import celery
import logging
log = logging.getLogger(__name__)
log.info('Testing logging outside Celery task')

logger = celery.utils.log.get_task_logger(__name__)

@celery.task
def glacier_restore(itemid,path):
    from boto.s3.connection import S3Connection
    conn = S3Connection('AKIAJXSAJRQLV3ERJLRA', 'g+3wrhtIvdylS2zh0xtnnogSiEWs4zLzPGoxytw6')
    logger.info("Attempting to connect to S3")
    logger.info("Item is "+itemid)
    logger.info("Path is "+path)
    return 'Finished'



