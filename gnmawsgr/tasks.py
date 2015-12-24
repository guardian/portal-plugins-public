import celery
import logging
log = logging.getLogger(__name__)
log.info('Testing logging outside Celery task')

logger = celery.utils.log.get_task_logger(__name__)

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
    (headers,content) = agent.request(url,method=method,body=body,headers=headers)
    return (headers,content)

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

@celery.task
def glacier_restore(itemid,path):
    import time
    import os
    from boto.s3.connection import S3Connection
    conn = S3Connection('***REMOVED***', '***REMOVED***')
    logger.info("Attempting to connect to S3")

    bucket = conn.get_bucket('gnm-multimedia-deeparchive')
    key = bucket.get_key(path)
    key.restore(days=1)
    logger.info("Attempting to restore "+path+" from S3")
    time.sleep(5)
    key = bucket.get_key(path)
    if key.ongoing_restore is True:
        logger.info("Ongoing restore for "+path+" is working")
        time.sleep(14400)
        key = bucket.get_key(path)
        logger.info("Testing if "+path+" has been restored")
        if key.ongoing_restore is False and key.expiry_date is not None:
            key.get_contents_to_filename('/opt/cantemo/portal/portal/plugins/gnmawsgr/downloads/'+itemid)
            logger.info("Downloading file from S3 for "+itemid)
            time.sleep(20)
            fsn = os.path.getsize('/opt/cantemo/portal/portal/plugins/gnmawsgr/downloads/'+itemid)
            fst = key.size
            logger.info("Testing if file for "+itemid+" has finished downloading from S3")
            if fsn == fst:
                logger.info("Making new shape for "+itemid)
                makeshape(itemid,'/opt/cantemo/portal/portal/plugins/gnmawsgr/downloads/'+itemid)
                return 'Restore job completed successfully'
            else:
                while fsn != fst:
                    logger.info("File for "+itemid+" still downloading from S3. Waiting one minute.")
                    time.sleep(60)
                    fsn = os.path.getsize('/opt/cantemo/portal/portal/plugins/gnmawsgr/downloads/'+itemid)
                    logger.info("Testing if file for "+itemid+" has finished downloading from S3")
                    if fsn == fst:
                        logger.info("Making new shape for "+itemid)
                        makeshape(itemid,'/opt/cantemo/portal/portal/plugins/gnmawsgr/downloads/'+itemid)
                        return 'Restore job completed successfully'
        else:
            while key.ongoing_restore is True:
                logger.info("Waiting an extra ten minutes")
                time.sleep(600)
                key = bucket.get_key(path)
                logger.info("Testing if "+path+" has been restored")
                if key.ongoing_restore is False and key.expiry_date is not None:
                    key.get_contents_to_filename('/opt/cantemo/portal/portal/plugins/gnmawsgr/downloads/'+itemid)
                    logger.info("Downloading file from S3 for "+itemid)
                    time.sleep(20)
                    fsn = os.path.getsize('/opt/cantemo/portal/portal/plugins/gnmawsgr/downloads/'+itemid)
                    fst = key.size
                    logger.info("Testing if file for "+itemid+" has finished downloading from S3")
                    if fsn == fst:
                        logger.info("Making new shape for "+itemid)
                        makeshape(itemid,'/opt/cantemo/portal/portal/plugins/gnmawsgr/downloads/'+itemid)
                        return 'Restore job completed successfully'
                    else:
                        while fsn != fst:
                            logger.info("File for "+itemid+" still downloading from S3. Waiting one minute.")
                            time.sleep(60)
                            fsn = os.path.getsize('/opt/cantemo/portal/portal/plugins/gnmawsgr/downloads/'+itemid)
                            logger.info("Testing if file for "+itemid+" has finished downloading from S3")
                            if fsn == fst:
                                logger.info("Making new shape for "+itemid)
                                makeshape(itemid,'/opt/cantemo/portal/portal/plugins/gnmawsgr/downloads/'+itemid)
                                return 'Restore job completed successfully'
    else:
        logger.info("Ongoing restore for "+path+" is not working")
        return 'Restore job not started'
