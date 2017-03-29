import logging
from celery.schedules import crontab
from celery.decorators import periodic_task
from celery import Celery

app = Celery()

log = logging.getLogger(__name__)

pagerduty_url = 'https://events.pagerduty.com/generic/2010-04-15/create_event.json'


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


@periodic_task(run_every=(crontab(minute='*/10')), name="check_storage", ignore_result=True)
def check_storage():
    from gnmvidispine.vs_storage import VSStoragePathMap
    from django.conf import settings
    from models import StorageData, IncidentKeys
    import requests
    import json

    returnthis = "Under threshold:"

    log.info("check_storage run by Celery.")

    i = app.control.inspect()

    running = str(i.active())

    rnumber = running.count("check_storage")

    if rnumber > 1:
        return "Task aborted to avoid duplication"

    system_type = get_system_type()

    storage_data = VSStoragePathMap(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                                    user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD,
                                    run_as=settings.VIDISPINE_USERNAME)
    sd = {'data':'value', 'test':'value'}
    sd['map'] = map(lambda (k,v): v.__dict__, storage_data.items())

    for val in sd['map']:
        record = StorageData.objects.get(storage_id=val['name'])
        try:
            key = IncidentKeys.objects.get(storage_id=val['name'])
        except Exception as e:
            key = IncidentKeys.objects.create(storage_id=val['name'])

        integer_trigger_size = int(record.trigger_size)
        integer_free_capacity = int(val['freeCapacity'])
        human_friendly_free_capacity = human_friendly(integer_free_capacity)
        integer_capacity = int(val['capacity'])
        percent_free_float = (100.0 / integer_capacity) * integer_free_capacity
        percent_free = int(percent_free_float)

        if integer_free_capacity < integer_trigger_size:

            returnthis = returnthis + " " + val['name']
            if key.incident_key == '':

                payload = {
                    "service_key": settings.PAGERDUTY_KEY,
                    "event_type": "trigger",
                    "description": "Storage {0} lacks sufficient free space. It is {1}% full.".format(val['contentDict']['name'],percent_free),
                    "details": {
                        "Vidispine ID": val['name'],
                        "Name": val['contentDict']['name'],
                        "Free Capacity": human_friendly_free_capacity,
                        "System Type": system_type
                        },
                }

                r = requests.post(pagerduty_url, data=json.dumps(payload))

                pddata = json.loads(r.text)

                key.incident_key = pddata['incident_key']
                key.save()

        else:

            if key.incident_key != '':

                payload = {
                    "service_key": settings.PAGERDUTY_KEY,
                    "event_type": "resolve",
                    "description": "Storage {0} no longer lacks sufficient free space. It is {1}% full.".format(val['contentDict']['name'],percent_free),
                    "incident_key": key.incident_key,
                    "details": {
                        "Vidispine ID": val['name'],
                        "Name": val['contentDict']['name'],
                        "Free Capacity": human_friendly_free_capacity,
                        "System Type": system_type,
                        "Space Used when Resolved": "{0}%".format(percent_free),
                        },
                }

                r = requests.post(pagerduty_url, data=json.dumps(payload))

                if r.status_code == 200:
                    key.incident_key = ''
                    key.save()


    if returnthis is "Under threshold:":
        returnthis = "No storages are under their thresholds."

    return returnthis
