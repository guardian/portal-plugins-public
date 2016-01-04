import celery
import logging
log = logging.getLogger(__name__)
log.info('Testing logging outside Celery task')

logger = celery.utils.log.get_task_logger(__name__)

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
    from django.conf import settings
    import re
    auth = base64.encodestring('%s:%s' % (settings.VIDISPINE_USERNAME, settings.VIDISPINE_PASSWORD)).replace('\n', '')

    headers['Authorization']="Basic %s" % auth
    headers['Content-Type']=content_type

    if not re.match(r'^/',urlpath):
        urlpath = '/' + urlpath

    url = "{0}:{1}{2}".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,urlpath)
    #url = "http://dc1-mmmw-05.dc1.gnm.int:8080{0}".format(urlpath)
    logging.debug("URL is %s" % url)
    (rtn_headers,content) = agent.request(url,method=method,body=body,headers=headers)
    if int(headers['status']) < 200 or int(headers['status']) > 299:
        raise HttpError(int(headers['status']),url,headers,rtn_headers,content)
    return (rtn_headers,content)

def makeshape(itemid,uri,agent=None):
    import json
    if agent is None:
        import httplib2
        agent = httplib2.Http()

    url = "/item/{0}/shape?uri={1}".format(itemid,uri)

    (headers,content) = make_vidispine_request(agent,"POST",url,body="",headers={'Accept': 'application/json'})
    if int(headers['status']) < 200 or int(headers['status']) > 299:
        #logging.error(content)
        #raise StandardError("Vidispine error: %s" % headers['status'])
        return None

    return json.loads(content)


class MiniItem(object):
    def __init__(self,raw_json):
        import json
        if isinstance(raw_json,basestring):
            self._data_content = json.loads(raw_json)
        elif isinstance(raw_json,dict):
            self._data_content = raw_json
        else:
            raise TypeError

    def get(self, fieldname, allow_list=True, delim=','):
        """
        Returns the metadata for fieldname, or raises KeyError if it's not present
        :param fieldname: field to get
        :param allow_list: if True, return multiple values as a list. If False, use delim to return as a string
        :param delim: if allow_list is False, use this as a delimiter to concatenate results. Defaults to ','
        :return: the requested metadata value
        """
        for timespan in self._data_content['item'][0]['metadata']['timespan']:
            for field in timespan['field']:
                if field['name'] == fieldname:
                    value_list = map(lambda x: x['value'], field['value'])
                    if allow_list:
                        return value_list
                    return delim.join(value_list)
        raise KeyError(fieldname)

def download_callback(current_progress,total):
    logger.info("Download in progress: {0}/{1}, {2}%%".format(current_progress,total,float(current_progress)/float(total)))

@celery.task
def glacier_restore(itemid,path):
    import time
    import json
    import os
    from django.conf import settings
    from boto.s3.connection import S3Connection
    from boto.exception import S3ResponseError
    from models import RestoreRequest
    from datetime import datetime
    import httplib2
    import traceback

    temp_path = "/opt/cantemo/portal/portal/plugins/gnmawsgr/downloads/"
    restore_time = 2 #in days
    restore_sleep_delay = 14400 #wait this number of seconds for something to restore

    if hasattr(settings,'glacier_temp_path'):
        temp_path = settings.glacier_temp_path
    if hasattr(settings,'glacier_restore_time'):
        temp_path = settings.glacier_restore_time

    interesting_fields = [
        'title',
        'gnm_external_archive_external_archive_device',
        'gnm_external_archive_external_archive_path',
        'gnm_external_archive_external_archive_report'
    ]
    agent = httplib2.Http()
    headers, content = make_vidispine_request(agent,"GET","/API/item/{id}/metadata?fields={fieldlist}"
                                              .format(itemid,','.join(interesting_fields)),
                                              body="",
                                              headers={'Accept': 'application/json'},
                                              )
    item_meta = MiniItem(content)

    try:
        rq = RestoreRequest.objects.get(item_id=itemid)
    except RestoreRequest.DoesNotExist:
        rq = RestoreRequest()
        rq.requested_at = datetime.now()
        rq.item_id = itemid
        rq.attempts = 0
        rq.status = 'READY'
        rq.save()

    logger.info("Attempting to contact S3")
    if hasattr(settings,'aws_access_key_id') and hasattr(settings, 'aws_secret_access_key'):
        conn = S3Connection(settings.aws_access_key_id, settings.aws_secret_access_key)
    else:
        conn = S3Connection()

    bucket = conn.get_bucket(item_meta.get('gnm_external_archive_external_archive_device'))
    key = bucket.get_key(path)

    if key.storage_class != 'GLACIER':
        logger.info("Item {0} ({1}) is not in Glacier so not attempting to restore".format(itemid,item_meta.get('title')))
        rq.status = 'NOT_GLACIER'
        rq.attempts = 0
        rq.completed_at = datetime.now()
        rq.save()
        return

    filename = os.path.join(temp_path, os.path.basename(item_meta.get('gnm_external_archive_external_archive_path')))
    try:
        with open(filename,'wb') as fp:
            key.get_file(fp, cb=download_callback, num_cb=100)
            post_restore_actions(itemid,filename)
    except S3ResponseError as e:
        try:
            #most likely, the asset is archived
            if rq.status != 'AWAITING_RESTORE':
                #we have not yet issued a restore request
                key.restore(restore_time)
                rq.status = 'AWAITING_RESTORE'
                rq.save()
                glacier_restore.apply_async((itemid, path), countdown=restore_sleep_delay)
                return
            else:
                #in this case, a restore request is pending.  Log a warning and wait.
                timediff = datetime.now() - rq.requested_at
                logger.warning("Glacier request for {0} has not completed in a timely way. Requested {0} ago.".format(timediff))
                glacier_restore.apply_async((itemid, path), countdown=600)
                return

        except S3ResponseError as e:
            #restore request failed, so there's something wrong with the object
            rq.status = 'FAILED'
            rq.completed_at = datetime.now()
            logger.error(e)
            logger.error(traceback.format_exc())


def post_restore_actions(itemid, downloaded_filename):
    logger.info("Creating shape for {0}...".format(itemid))
    makeshape(itemid,downloaded_filename)
    logger.info("Done.")
