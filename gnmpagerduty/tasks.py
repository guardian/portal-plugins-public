#import celery
import logging
from django.conf import settings
from gnmvidispine.vs_storage import VSStoragePathMap
from celery.schedules import crontab
from celery.decorators import periodic_task
from celery import Celery
app = Celery()


log = logging.getLogger(__name__)
log.info('Testing logging outside Celery task. PagerDuty.')

#try:
#    logger = celery.utils.log.get_task_logger(__name__)
#except AttributeError:
#    logger = logging.getLogger('main')

logger = logging.getLogger('main')

#settings.PAGERDUTY_KEY

#@celery.task
@periodic_task(run_every=(crontab(minute='*/10')), name="check_storage", ignore_result=True)
def check_storage():
    from pprint import pprint
    from models import StorageData, IncidentKeys
    import requests
    import json

    logger.info("check_storage run by Celery.")

    i = app.control.inspect()
    print i.active()

    running = str(i.active())

    rnumber = running.count("check_storage")

    if rnumber > 1:
        return "Task aborted to avoid duplication"

    storage_data = VSStoragePathMap(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                                    user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD,
                                    run_as=settings.VIDISPINE_USERNAME)
    sd = {'data':'value', 'test':'value'}
    sd['map'] = map(lambda (k,v): v.__dict__, storage_data.items())

    returnthis = "Under threshold:"

    url = 'https://events.pagerduty.com/generic/2010-04-15/create_event.json'

    n = 0

    for val in sd['map']:
        print(val['name'])
        try:
            record = StorageData.objects.get(storage_id=val['name'])
            try:
                key = IncidentKeys.objects.get(storage_id=val['name'])
            except Exception as e:
                key = IncidentKeys.objects.create(storage_id=val['name'])

            print(record.__dict__)
            print record.trigger_size
            print val['freeCapacity']
            if key.incident_key != '':
                print "Old key: ", key.incident_key

            intts = int(record.trigger_size)
            intfc = int(val['freeCapacity'])

            if intfc < intts:
                print 'Running at point one'
                returnthis = returnthis + " " + val['name']
                if key.incident_key == '':
                    print 'Running at point two'
                    payload = {
                        "service_key": settings.PAGERDUTY_KEY,
                        "event_type": "trigger",
                        "description": "Storage {0} lacks sufficient free space".format(val['contentDict']['name']),
                        #"client": "GNM PagerDuty",
                        #"client_url": "https://monitoring.service.com",
                        "details": {
                            "Vidispine ID": val['name'],
                            "Name": val['contentDict']['name'],
                            "Free Capacity": val['freeCapacity']
                            },
                        #"contexts":[
                        #    {
                        #    "type": "link",
                        #    "href": "http://acme.pagerduty.com"
                        #    },{
                        #    "type": "link",
                        #    "href": "http://acme.pagerduty.com",
                        #    "text": "View the incident on PagerDuty"
                        #    }
                        #]
                    }

                    r = requests.post(url, data=json.dumps(payload))

                    pddata = json.loads(r.text)

                    key.incident_key = pddata['incident_key']
                    key.save()

                    print r.text
                    print r.status_code
            else:
                print 'Running at point three'
                if key.incident_key != '':

                    print 'Running at point four'

                    payload = {
                        "service_key": settings.PAGERDUTY_KEY,
                        "event_type": "resolve",
                        "description": "Storage {0} no longer lacks sufficient free space".format(val['contentDict']['name']),
                        #"client": "GNM PagerDuty",
                        "incident_key": key.incident_key,
                        "details": {
                            "Vidispine ID": val['name'],
                            "Name": val['contentDict']['name'],
                            "Free Capacity": val['freeCapacity']
                            },
                    }

                    r = requests.post(url, data=json.dumps(payload))

                    print r.text
                    print r.status_code

                    if r.status_code == 200:
                        print 'Running at point five'
                        key.incident_key = ''
                        key.save()

        except Exception as e:
            print 'try code went wrong'

        n = (n + 1)

    if returnthis is "Under threshold:":
        returnthis = "No storages are under their thresholds."

    return returnthis
