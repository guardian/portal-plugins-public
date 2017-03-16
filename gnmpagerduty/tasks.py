#import celery
import logging
from django.conf import settings
from gnmvidispine.vs_storage import VSStoragePathMap
from celery.schedules import crontab
from celery.decorators import periodic_task

log = logging.getLogger(__name__)
log.info('Testing logging outside Celery task. PagerDuty.')

#try:
#    logger = celery.utils.log.get_task_logger(__name__)
#except AttributeError:
#    logger = logging.getLogger('main')

logger = logging.getLogger('main')

#@celery.task
@periodic_task(run_every=(crontab(minute='*/10')), name="check_storage", ignore_result=True)
def check_storage():
    from pprint import pprint
    from models import StorageData

    logger.info("check_storage run by Celery.")

    storage_data = VSStoragePathMap(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                                    user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD,
                                    run_as=settings.VIDISPINE_USERNAME)
    sd = {'data':'value', 'test':'value'}
    sd['map'] = map(lambda (k,v): v.__dict__, storage_data.items())

    returnthis = "Over threshold:"

    n = 0

    for val in sd['map']:
        print(val['name'])
        try:
            record = StorageData.objects.get(storage_id=val['name'])
            pprint(record)
            print record.trigger_size
            print val['freeCapacity']
            #sd['map'][n]['triggerSize'] = int(record.trigger_size)
            if val['freeCapacity'] < record.trigger_size:
                returnthis = returnthis + " " + val['name']

        except Exception as e:
            print 'try code went wrong'

        n = (n + 1)

    #check_storage.apply_async(countdown=600, retry=False)
    #return '{0} {1} {2} {3} {4} {5} {6} {7}'.format(sd['map'][0]['name'],sd['map'][1]['name'],sd['map'][2]['name'],sd['map'][3]['name'],sd['map'][4]['name'],sd['map'][5]['name'],sd['map'][6]['name'],sd['map'][7]['name'])
    return returnthis
