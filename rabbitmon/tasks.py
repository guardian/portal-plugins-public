from celery import shared_task
import logging
from indexing_ops import INDEXNAME, DOCTYPE

logger = logging.getLogger(__name__)


class HttpBasicAuth(object):
    def __init__(self,user,password):
        self._user = user
        self._password = password

    def header_content(self):
        from base64 import b64encode
        return 'Basic ' + b64encode('{u}:{p}'.format(u=self._user,p=self._password))


class HttpError(StandardError):
    def __init__(self,headers,content):
        self._headers = headers
        self.content = content

    def __str__(self):
        return "HTTP error {e}".format(e=self._headers['status'])


def get_rabbitmq_stats(user,password):
    import httplib2
    import json


    h = httplib2.Http()
    a = HttpBasicAuth(user,password)

    headers = {
        'Authorization': a.header_content(),
        'Accept': 'application/json'
    }

    (rtn_headers,content) = h.request("http://localhost:15672/api/queues/portal",headers=headers)
    status = int(rtn_headers['status'])
    if status<200 or status>299:
        raise HttpError(rtn_headers,content)
    return json.loads(content)


def breakdown_celery_info(infolist):
    rtn = {}
    for entry in infolist:
        rtn[entry['name']] = entry

    return rtn


def elastic_action_list(infolist,timestamp):
    from django.conf import settings
    actions = []
    for entry in infolist:
        rec = entry
        rec.update({
            '@timestamp': timestamp,
        })
        actions.append({
            '_op_type': 'index',
            '_index': INDEXNAME,
            '_type': DOCTYPE,
            '_source': rec,
        })
    return actions


@shared_task
def update_rabbitmq_stats():
    from django.conf import settings
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk, BulkIndexError
    import socket
    from pprint import pprint
    from datetime import datetime

    raven_client = None
    try:
        from raven import Client
        raven_client = Client(settings.RAVEN_CONFIG['dsn'])
    except StandardError as e:
        logger.error("Unable to initialise Raven, exceptions will not be logged to Sentry.  Error was {0}".format(e))

    try:
        info = get_rabbitmq_stats(settings.DATABASES['default']['USER'],settings.DATABASES['default']['PASSWORD'])
        #pprint(info)
    except socket.error as e:
        logger.error("Unable to connect to socket.  Is the rabbitmq management plugin installed?")
        if raven_client is not None: raven_client.captureException()
        return
    except HttpError as e:
        logger.error("Rabbitmq management plugin returned {0}".format(str(e)))
        logger.error(e.content)
        if raven_client is not None: raven_client.captureException()
        return

    # FIXME: how to get default elastic cluster address?
    esclient = Elasticsearch(hosts=['127.0.0.1:9200'])

    if not esclient.indices.exists(index=INDEXNAME):
        esclient.indices.create(index=INDEXNAME)

    actionlist = elastic_action_list(info, datetime.now())
    (n_success, errorlist) = bulk(esclient, actionlist)

    if n_success<len(actionlist):
        logger.error("{0} elasticsearch actions failed".format(len(actionlist) - n_success))
        if raven_client is not None: raven_client.captureMessage("{0}".format(str(errorlist)))
        for err in errorlist:
            logger.error(err)

