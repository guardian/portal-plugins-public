import logging
from django.conf import settings
from gnmvidispine.vs_storage import VSStoragePathMap
from celery.schedules import crontab
from celery.decorators import periodic_task
from celery import Celery
app = Celery()


log = logging.getLogger(__name__)

logger = logging.getLogger('main')


@periodic_task(run_every=(crontab(minute='*/10')), name="check_storage", ignore_result=True)
def check_storage():
    from models import StorageData, IncidentKeys
    import requests
    import json

    logger.info("check_storage run by Celery.")

    i = app.control.inspect()

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

    for val in sd['map']:

        try:
            record = StorageData.objects.get(storage_id=val['name'])
            try:
                key = IncidentKeys.objects.get(storage_id=val['name'])
            except Exception as e:
                key = IncidentKeys.objects.create(storage_id=val['name'])

            intts = int(record.trigger_size)
            intfc = int(val['freeCapacity'])

            if intfc < intts:

                returnthis = returnthis + " " + val['name']
                if key.incident_key == '':

                    payload = {
                        "service_key": settings.PAGERDUTY_KEY,
                        "event_type": "trigger",
                        "description": "Storage {0} lacks sufficient free space".format(val['contentDict']['name']),
                        "details": {
                            "Vidispine ID": val['name'],
                            "Name": val['contentDict']['name'],
                            "Free Capacity": val['freeCapacity']
                            },
                    }

                    r = requests.post(url, data=json.dumps(payload))

                    pddata = json.loads(r.text)

                    key.incident_key = pddata['incident_key']
                    key.save()

            else:

                if key.incident_key != '':

                    payload = {
                        "service_key": settings.PAGERDUTY_KEY,
                        "event_type": "resolve",
                        "description": "Storage {0} no longer lacks sufficient free space".format(val['contentDict']['name']),
                        "incident_key": key.incident_key,
                        "details": {
                            "Vidispine ID": val['name'],
                            "Name": val['contentDict']['name'],
                            "Free Capacity": val['freeCapacity']
                            },
                    }

                    r = requests.post(url, data=json.dumps(payload))

                    if r.status_code == 200:

                        key.incident_key = ''
                        key.save()

        except Exception as e:
            print 'An error occurred'

    if returnthis is "Under threshold:":
        returnthis = "No storages are under their thresholds."

    return returnthis
