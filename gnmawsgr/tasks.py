import celery
import logging
log = logging.getLogger(__name__)
log.info('Testing logging outside Celery task')

logger = celery.utils.log.get_task_logger(__name__)

@celery.task
def glacier_restore(itemid,path):
    import time
    from boto.s3.connection import S3Connection
    conn = S3Connection('AKIAJXSAJRQLV3ERJLRA', 'g+3wrhtIvdylS2zh0xtnnogSiEWs4zLzPGoxytw6')
    logger.info("Attempting to connect to S3")

    bucket = conn.get_bucket('gnm-multimedia-deeparchive')
    key = bucket.get_key(path)
    key.restore(days=1)
    logger.info("Attempting to restore "+path+" from S3")
    time.sleep(5)
    key = bucket.get_key(path)
    if key.ongoing_restore is True:
        logger.info("Ongoing restore for "+path+" is working")
    else:
        logger.info("Ongoing restore for "+path+" is not working")
    return 'Finished'



