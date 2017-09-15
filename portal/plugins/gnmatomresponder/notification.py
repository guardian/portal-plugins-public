from xml.etree.cElementTree import fromstring, tostring
import lxml.etree
from django.core.urlresolvers import reverse
import logging
from requests import get,post
from django.conf import settings
from requests.auth import HTTPBasicAuth
from time import sleep

logger = logging.getLogger(__name__)


def _get_callback_url(use_auth=None):
    if use_auth is None:
        auth = False
    else:
        auth = True

    try:
        from django.conf import settings
        r = get('%s:%s/whatismyipaddress/' % (settings.VIDISPINE_URL, settings.VIDISPINE_PORT), headers={'Accept': 'text/plain'})
        if r.status_code < 300:
            # TODO auto-detect https
            if auth:
                return 'http://' + settings.VIDISPINE_USERNAME + ':' + settings.VIDISPINE_PASSWORD + '@' + r.text.strip() + '/'
            return 'http://' + r.text.strip() + '/'
    except Exception as x:
        logger.error(x)

    # use callback from settings
    if hasattr(settings, "PLUTO_CALLBACK_URL"):
        v = settings.PLUTO_CALLBACK_URL
    else:
        # fallback to vidispine address
        raise RuntimeError("Unable to determine callback server address")
    v = v.strip()
    logger.warn('Failed to auto-detect IP address. Reverting to %s' % v)
    if not v.endswith('/'):
        v = v + '/'
    if auth and v.startswith('http://'):
        v = 'http://' + settings.VIDISPINE_USERNAME + ':' + settings.VIDISPINE_PASSWORD + '@' + v[7:]
    elif auth and v.startswith('https://'):
        v = 'https://' + settings.VIDISPINE_USERNAME + ':' + settings.VIDISPINE_PASSWORD + '@' + v[8:]
    else:
        pass
    return v


def create_notification(retries=10,sleep_delay=10):
    """
    Creates a Vidispine notification for completed imports
    :return: None. Raises a RuntimeException if we could not set up the notification.
    """
    notification_doc = u"""<?xml version="1.0" encoding="UTF-8"?>
    <NotificationDocument xmlns="http://xml.vidispine.com/schema/vidispine">
    <action>
        <http synchronous="false" group="atom_notifications">
            <url>{myaddress}{uri}</url>
            <contentType>application/xml</contentType>
            <method>POST</method>
            <timeout>60</timeout>
            <retry>10</retry>
        </http>
    </action>

    <trigger>
        <job>
            <stop/>
            <filter>
                <!-- check this, might be a different type -->
                <type>RAW_IMPORT</type>
                <type>ESSENCE_VERSION</type>
                <jobdata>
                    <key>gnm_source</key>
                    <value>media_atom</value>
                </jobdata>
            </filter>
        </job>
    </trigger>
    </NotificationDocument>
    """

    doc_to_send = notification_doc.format(
        uri="/gnmatomresponder/jobnotify",
        myaddress=_get_callback_url().rstrip('/')
    )
    logger.debug("doc to send: {0}".format(doc_to_send))

    output_url = "{0}:{1}/API/job/notification".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT)

    n=0
    while True:
        n+=1
        response = post(output_url,data=doc_to_send,
                        headers={'Accept': 'application/xml', 'Content-Type': 'application/xml'},
                        auth=HTTPBasicAuth(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD))
        if response.status_code>199 or response.status_code<299:
            break
        if n>retries:
            raise RuntimeError("Unable to create vidispine notification ({0}): {1}".format(response.status_code, response.content))
        sleep(sleep_delay)


def safe_get(uri,retries=10,sleep_delay=10):
    """
    Makes a Get request to Vidispine, retrying if we get an invalid response.
    :param uri:
    :param retries:
    :param sleep_delay:
    :return:
    """
    n=0
    while True:
        n+=1
        response = get(uri,headers={'Accept': 'application/xml'}, auth=HTTPBasicAuth(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD))
        if response.status_code>199 or response.status_code<299:
            return response
        if n>retries:
            raise RuntimeError("Unable to search vidispine notification ({0}): {1}".format(response.status_code, response.content))
        sleep(sleep_delay)


ns = "{http://xml.vidispine.com/schema/vidispine}"


def check_notification_at(uri,retries=10,sleep_delay=10):
    """
    Checks whether the givien notification URI is "one of ours".
    We need to do this with lxml, as xml.etree.cElementTree does not properly support .. in xpath expressions.
    :param uri: URI to check
    :return: True if it is one of ours, False if not.
    """
    response = safe_get(uri, retries=retries, sleep_delay=sleep_delay)

    encoded_response = response.content.encode('UTF-8')
    parser = lxml.etree.XMLParser(ns_clean=False, recover=True, encoding='UTF-8')
    notification_doc = lxml.etree.fromstring(encoded_response, parser=parser)

    def find_value_for_key(xmlnode,key):
        n=0
        for node in xmlnode.findall('{0}trigger/{0}job/{0}filter/{0}jobdata/{0}key'.format(ns)):
            n+=1
            if node.text==key:
                valnode = node.find('../{0}value'.format(ns))
                if valnode is not None:
                    return valnode.text
                return None
        return None

    appname = find_value_for_key(notification_doc,"gnm_source")
    if appname and appname=="media_atom":
        return True
    return False


def find_notification(retries=10,sleep_delay=10):
    """
    Look up whether the notification exists in the Vidispine system
    :param retries:
    :param sleep_delay:
    :return: URI of the notification, or None if it does not exist.
    """
    output_url = "{0}:{1}/API/job/notification".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT)

    response = safe_get(output_url, retries=retries,sleep_delay=sleep_delay)

    print response.content
    notification_list = fromstring(response.content)
    for urinode in notification_list.findall('{0}uri'.format(ns)):
        if check_notification_at(urinode.text):
            return urinode.text
    return None


def process_notification(notification):
    from models import ImportJob
    importjob = ImportJob.objects.get(job_id=notification.jobId)
    importjob.status = notification.status
    importjob.save()