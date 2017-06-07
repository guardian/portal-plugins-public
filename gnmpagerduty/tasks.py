import logging
from celery.schedules import crontab
from celery.decorators import periodic_task
from celery import Celery

log = logging.getLogger('main')

pagerduty_url = 'https://events.pagerduty.com/generic/2010-04-15/create_event.json'

MAX_RETRIES = 20    #max number of times to retry talking to pagerduty
INITIAL_DELAY = 1   #initial wait time
DELAY_FACTOR = 2    #multiply wait time by this every time it fails

def human_friendly(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class HttpError(StandardError):
    def __init__(self, code, url, headers, rtn_headers, rtn_body, *args, **kwargs):
        super(HttpError,self).__init__(*args,**kwargs)
        self.code = code
        self.url = url
        self.headers = headers
        self.rtn_headers = rtn_headers
        self.rtn_body = rtn_body

    def __unicode__(self):
        return u'HTTP error accessing {url}: {code}. Server said {rtn_body}'.format(
            url=self.url,
            code=self.code,
            rtn_body=self.rtn_body
        )

    def __str__(self):
        return self.__unicode__().encode('ascii')


def make_vidispine_request(agent,method,urlpath,body,headers,content_type='application/xml'):
    import base64
    import re
    from django.conf import settings
    auth = base64.encodestring('%s:%s' % (settings.VIDISPINE_USERNAME, settings.VIDISPINE_PASSWORD)).replace('\n', '')

    headers['Authorization']="Basic %s" % auth
    headers['Content-Type']=content_type

    if not re.match(r'^/',urlpath):
        urlpath = '/' + urlpath

    url = "{0}:{1}{2}".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,urlpath)

    (rtn_headers,content) = agent.request(url,method=method,body=body,headers=headers)
    if int(rtn_headers['status']) < 200 or int(rtn_headers['status']) > 299:
        raise HttpError(int(rtn_headers['status']),url,headers,rtn_headers,content)
    return (rtn_headers,content)


def get_system_type():
    from django.core.cache import cache
    import httplib2
    system_type = cache.get('gnmpagerduty_system_type')
    if system_type is None:
        h=httplib2.Http()
        headers, content = make_vidispine_request(h,'GET','/API/site?type=current',"",{'Accept': 'application/json'})

        output = str(content)

        if "KP" in output:
            system_type = 'Live'
        elif "BK" in output:
            system_type = 'DC2'
        elif "VX" in output:
            system_type = 'Development'
        else:
            system_type = 'Unknown'
        cache.set('gnmpagerduty_system_type', system_type)
    return system_type


def return_percentage(integer_capacity, integer_free_capacity):
    percent_free_float = (100.0 / integer_capacity) * integer_free_capacity
    return int(percent_free_float)


def notify_pagerduty(message, event_type, incident_key, vidis_id=None,storage_name=None,free_capacity=None,system_type=None):
    import requests
    import json
    from django.conf import settings

    payload = {
        "service_key": settings.PAGERDUTY_KEY,
        "event_type": event_type,
        "incident_key": incident_key,
        "description": message,
        "details": {
            "Vidispine ID": vidis_id,
            "Name": storage_name,
            "Free Capacity": free_capacity,
            "System Type": system_type
        }
    }

    r = requests.post(pagerduty_url, data=json.dumps(payload))
    if r.status_code<200 or r.status_code>299:
        raise HttpError(r.status_code,pagerduty_url,None,r.headers,r.content)

    pddata = r.json()
    return pddata


def storage_below_safelevel(key,val):
    """
    Called by the main task when a storage has dropped below the minimum safe level
    :param key: object from the incident_key model
    :param val: metadata returned from storage_data map about the storage
    :return: None
    """
    if key.incident_key == '':
        #if no incident has yet been registered, send one to PD
        percent_free = return_percentage(int(val['capacity']), int(val['freeCapacity']))

        pddata = notify_pagerduty("Storage {0} lacks sufficient free space. It is {1}% full.".format(val['contentDict']['name'],percent_free),
                         "trigger",
                         key.incident_key,
                         vidis_id=val['name'],
                         storage_name=val['contentDict']['name'],
                         free_capacity=human_friendly(int(val['freeCapacity'])),
                         system_type=get_system_type(),
                         )

        key.incident_key = pddata['incident_key']
        key.save()
    else:
        pass


def storage_above_safelevel(key, val):
    """
    Called by the main task when a storage is above the minimum safe level
    :param key: object from the incident_key model
    :param val: metadata returned from storage_data map about the storage
    :return: None
    """
    percent_free = return_percentage(int(val['capacity']), int(val['freeCapacity']))
    if key.incident_key != '':
        pddata = notify_pagerduty("Storage {0} no longer lacks sufficient free space. It is {1}% full.".format(val['contentDict']['name'],percent_free),
                                  "resolve",
                                  key.incident_key,
                                  vidis_id=val['name'],
                                  storage_name=val['contentDict']['name'],
                                  free_capacity=human_friendly(int(val['freeCapacity'])),
                                  system_type=get_system_type()
                                  )
        #if the HTTP request failed then we should have raised an exception
        key.incident_key = ''
        key.save()

@periodic_task(run_every=(crontab(minute='*/10')), name="check_storage", ignore_result=True)
def check_storage(celery_app=None):
    """
    Runs the main loop to check storages.  This is run as a periodic task by celery beat.
    :param celery_app: pass in a fake celery app instance, for testing.  In production usage, leave this out and it defaults to None
    :return: String indicating the system status, for celery flower
    """
    from gnmvidispine.vs_storage import VSStoragePathMap
    from django.conf import settings
    from models import StorageData, IncidentKeys
    from time import sleep

    log.info("check_storage run by Celery.")

    storage_data = VSStoragePathMap(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                                    user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD,
                                    run_as=settings.VIDISPINE_USERNAME)

    sd = {
        'map': map(lambda (k,v): v.__dict__, storage_data.items())
    }

    storages_below_thresold=[]

    for val in sd['map']:
        try:
            record = StorageData.objects.get(storage_id=val['name'])
        except StorageData.DoesNotExist:
            continue

        try:
            key = IncidentKeys.objects.get(storage_id=val['name'])
        except IncidentKeys.DoesNotExist:
            key = IncidentKeys.objects.create(storage_id=val['name'])

        integer_trigger_size = int(record.trigger_size)
        integer_free_capacity = int(val['freeCapacity'])

        attempt=0
        delay_time = INITIAL_DELAY
        while True:
            try:
                if integer_free_capacity < integer_trigger_size:
                    storage_below_safelevel(key,val)
                    storages_below_thresold.append(val['contentDict']['name'])
                else:
                    storage_above_safelevel(key,val)
                break
            except HttpError as e:
                if e.code==503 or e.code==500:
                    attempt+=1
                    if attempt>=MAX_RETRIES:
                        log.error("Unable to contact pagerduty after {0} attempts.".format(attempt))
                        raise
                    log.warning("Received {0} error trying to contact pagerduty. Trying again after {1} seconds...".format(e.code,delay_time))
                    sleep(delay_time)
                    delay_time*=2

    if len(storages_below_thresold)==0:
        return "No storages are under their thresholds."
    else:
        return "Storages below threshold: " + ",".join(storages_below_thresold)

