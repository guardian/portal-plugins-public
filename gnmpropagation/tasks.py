import celery
import logging
log = logging.getLogger(__name__)
log.info('Testing logging outside Celery task')

try:
    logger = celery.utils.log.get_task_logger(__name__)
except AttributeError:
    logger = logging.getLogger('main')


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
    logger.debug("URL is %s" % url)
    (rtn_headers,content) = agent.request(url,method=method,body=body,headers=headers)
    if int(rtn_headers['status']) < 200 or int(rtn_headers['status']) > 299:
        raise HttpError(int(rtn_headers['status']),url,headers,rtn_headers,content)
    return (rtn_headers,content)


def makeshape(itemid,uri,tagname='original',agent=None):
    import json
    import re
    if agent is None:
        import httplib2
        agent = httplib2.Http()

    if not re.match(r'^\w+:/',uri):
        uri = 'file:' + uri

    url = "/API/item/{0}/shape?uri={1}&tag={2}".format(itemid,uri,tagname)

    (headers,content) = make_vidispine_request(agent,"POST",url,body="",headers={'Accept': 'application/json'})

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

    def _descend_groups(self,data_hash,fieldname):
        #from pprint import pprint
        #pprint(data_hash)
        if not 'group' in data_hash or not isinstance(data_hash['group'],list):
            return

        for g in data_hash['group']:
            #pprint(g)
            for field in g['field']:
                #print "checking field {0}".format(field['name'])
                if field['name'] == fieldname:
                    value_list = map(lambda x: x['value'], field['value'])
                    return value_list
            if 'group' in g:
                result = self._descend_groups(g,fieldname)
                if result is not None:
                    return result

    def get(self, fieldname, allow_list=True, delim=','):
        """
        Returns the metadata for fieldname, or raises KeyError if it's not present
        :param fieldname: field to get
        :param allow_list: if True, return multiple values as a list. If False, use delim to return as a string
        :param delim: if allow_list is False, use this as a delimiter to concatenate results. Defaults to ','
        :return: the requested metadata value
        """
        for timespan in self._data_content['item'][0]['metadata']['timespan']:
            value_list = None
            for field in timespan['field']:
                if field['name'] == fieldname:
                    value_list = map(lambda x: x['value'], field['value'])
            if value_list is None:
                value_list = self._descend_groups(timespan,fieldname)
            if value_list is not None:
                if len(value_list) == 1:
                    return value_list[0]
                if allow_list:
                    return value_list
                return delim.join(value_list)
        raise KeyError(fieldname)

    def valid_fields(self):
        """
        Generator which yields the valid field names
        :return:
        """
        for timespan in self._data_content['item'][0]['metadata']['timespan']:
            for field in timespan['field']:
                yield field['name']


def download_callback(rq, current_progress,total):
    if rq.status != 'DOWNLOADING':
        rq.status = 'DOWNLOADING'
    logger.info("{itemid} Download in progress: {cur}/{tot}, {pc:.2f}%".format(
        itemid=rq.item_id,
        cur=current_progress,
        tot=total,
        pc=100*float(current_progress)/float(total)))
    rq.currently_downloaded = current_progress
    rq.file_size = total
    rq.save()


#@celery.task
def propagate(collectionid,field,switch):
    #from models import RestoreRequest
    from vidispine.vs_collection import VSCollection
    import traceback
    try:
        import raven
        from django.conf import settings
        raven_client = raven.Client(settings.RAVEN_CONFIG['dsn'])

    except StandardError as e:
        logger.error("Raven client either not installed (pip install raven) or set up (RAVEN_CONFIG in localsettings.py).  Unable to report errors to Sentry")
        raven_client = None

    print collectionid
    print field
    print switch


    if (0 == 1):

        try:
            do_glacier_restore(request_id,itemid,path)
        except StandardError as e:
            if raven_client: #if raven is set up, capture some extra information then grab the exception
                raven_client.user_context({'request_id': request_id, 'item_id': itemid, 'path': path})
                try:
                    from django.conf import settings
                    from vidispine.vs_item import VSItem
                    item_obj = VSItem(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
                    item_obj.populate(itemid,specificFields=['title','gnm_asset_category'])
                    rq = RestoreRequest.objects.get(pk=request_id)
                    rq.status = "FAILED"
                    rq.failure_reason = u"{0}\n{1}".format(unicode(e),traceback.format_exc())
                    rq.save()
                    item_obj.set_metadata({'gnm_asset_status': 'Archived to External'})
                    raven_client.user_context({'request_id': request_id, 'request_details': rq.__dict__,
                                               'item_id': itemid, 'path': path})
                except StandardError as e: #if the database is playing silly buggers then log that too.
                    raven_client.captureException()
                    logger.error(e)
                    logger.error(traceback.format_exc())
                raven_client.captureException()

            logger.error(e)
            logger.error(traceback.format_exc())
            raise #re-raise the exception, so it shows as Failed in Celery Flower


def do_glacier_restore(request_id,itemid,path):
    import os
    from django.conf import settings
    from boto.s3.connection import S3Connection
    from boto.exception import S3ResponseError
    from models import RestoreRequest
    from datetime import datetime
    from vidispine.vs_item import VSItem
    import httplib2
    import traceback
    from functools import partial

    temp_path = "/tmp"
    restore_time = 2 #in days
    restore_sleep_delay = 14400 #wait this number of seconds for something to restore
    restore_short_delay = 600

    if hasattr(settings,'GLACIER_TEMP_PATH'):
        temp_path = settings.GLACIER_TEMP_PATH
    if hasattr(settings,'GLACIER_RESTORE_TIME'):
        restore_time = settings.GLACIER_RESTORE_TIME

    interesting_fields = [
        'title',
        'gnm_external_archive_external_archive_device',
        'gnm_external_archive_external_archive_path',
        'gnm_external_archive_external_archive_status',
        'gnm_external_archive_external_archive_report',
    ]
    agent = httplib2.Http()

    try:
        headers, content = make_vidispine_request(agent,"GET","/API/item/{id}/metadata?fields={fieldlist}"
                                                  .format(id=itemid,fieldlist=','.join(interesting_fields)),
                                                  "",
                                                  {'Accept': 'application/json'},
                                                  )
    except HttpError as e:
        if e.code == 404:
            logger.error("Item {0} does not exist".format(itemid))
        else:
            logger.error(e)
        return

    item_meta = MiniItem(content)

    item_obj = VSItem(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
    item_obj.populate(itemid,specificFields=['title','gnm_asset_category'])
    rq = RestoreRequest.objects.get(pk=request_id)

    logger.info("Attempting to contact S3")
    if hasattr(settings, 'AWS_ACCESS_KEY_ID') and hasattr(settings, 'AWS_SECRET_ACCESS_KEY'):
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    else:
        raise StandardError("No credentials in settings")
        conn = S3Connection()

    checksum = "(not found)"
    try:
        bucket = conn.get_bucket(item_meta.get('gnm_external_archive_external_archive_device'))
        key = bucket.get_key(path)

    except KeyError:
        logger.error("Item {0} ({1}) does not appear to have gnm_external_archive_external_archive_device set".format(itemid,item_meta.get('title')))
        rq.status = 'FAILED'
        rq.completed_at = datetime.now()
        rq.save()
        return

    filename = os.path.join(temp_path, os.path.basename(item_meta.get('gnm_external_archive_external_archive_path')))
    n=0
    while True:
        try:
            with open(filename,'wb') as fp:
                key.get_file(fp, cb=partial(download_callback, rq), num_cb=40)
            rq.completed_at = datetime.now()
            rq.status = 'IMPORTING'
            rq.file_size_check = "Expected: {0} bytes. Actual: {1} bytes.".format(rq.file_size,os.path.getsize(filename))
            if (os.path.getsize(filename) + 20000) < rq.file_size:
                rq.status = "FAILED"
                rq.save()
                break
            rq.save()
            post_restore_actions(itemid,filename)
            rq.status = 'COMPLETED'
            rq.completed_at = datetime.now()
            rq.filepath_original = path
            rq.filepath_destination = filename
            rq.save()
            item_obj.set_metadata({'gnm_asset_status': 'Ready for Editing (from Archive)'})
            break

        except IOError as e:
            n+=1
            if n>20: #if we've already retried 20 times then give up
                raise
            logger.error(e)
            filename = filename + '-1'
            continue

        except S3ResponseError as e:
            try:
                logger.warning(e)
                #most likely, the asset is archived
                if rq.status != 'AWAITING_RESTORE':
                    item_obj.set_metadata({'gnm_asset_status': 'Waiting for Archive Restore'})
                    os.unlink(filename)
                    #we have not yet issued a restore request
                    key.restore(restore_time)
                    rq.status = 'AWAITING_RESTORE'
                    rq.file_size = key.size
                    rq.filepath_original = path
                    rq.filepath_destination = filename
                    rq.save()
                    glacier_restore.apply_async((rq.pk,itemid, path), countdown=restore_sleep_delay)
                    return
                else:
                    #in this case, a restore request is pending.  Log a warning and wait.
                    timediff = datetime.now() - rq.requested_at
                    logger.warning("Glacier request for {0} has not completed in a timely way. Requested {1} ago.".format(rq.item_id,timediff))
                    glacier_restore.apply_async((rq.pk,itemid, path), countdown=restore_short_delay)
                    return

            except S3ResponseError as e:
                #restore request failed, so there's something wrong with the object
                rq.status = 'FAILED'
                rq.completed_at = datetime.now()
                rq.save()
                item_obj.set_metadata({'gnm_asset_status': 'Archived to External'})
                logger.error(e)
                logger.error(traceback.format_exc())
                raise


def post_restore_actions(itemid, downloaded_filename):
    logger.info("Creating shape for {0}...".format(itemid))
    try:
        makeshape(itemid,downloaded_filename,tagname='original')
    except HttpError as e:
        logger.error(unicode(e))
        raise
    logger.info("Done.")

if __name__ == '__main__':
    import sys
    #Use this statment to test from command line
    for arg in sys.argv:
        print arg

    propagate(sys.argv[1],sys.argv[2],sys.argv[3])



