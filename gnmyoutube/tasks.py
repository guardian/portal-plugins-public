from celery import shared_task
from youtube_interface import YoutubeInterface
import logging

class VidispineError(StandardError):
    pass


def update_vidispine_field_values(fieldName,cats):
    import httplib2
    from django.conf import settings as portal_settings
    from xml.etree import ElementTree as ET
    import json
    from plugin import make_vidispine_request

    #step one - get Vidispine's field definition
    h = httplib2.Http()
    logging.debug("Looking up field {0}".format(fieldName))
    uri = "{0}:{1}/API/metadata-field/{2}?data=all".format(portal_settings.VIDISPINE_HOST,portal_settings.VIDISPINE_PORT,fieldName)

    (content,headers) = make_vidispine_request(h,"GET",uri,None,None)

    if int(headers['code']) < 200 or int(headers['code']) > 299:
        raise VidispineError(content)

    logging.debug("Loading data from document...")
    ns = "{http://xml.vidispine.com/schema/vidispine}"
    xmlData = ET.parse(content)
    #//data/key[text()="extradata"]/../value/
    portalDataNode = xmlData.find('{0}data/{0}key[text()="extradata"]/../{0}value'.format(ns))

    #step two - parse Portal's extradata field
    portalData = json.loads(portalDataNode.text)
    logging.debug("{0}".format(str(portalData)))

    #step 3 - replace the values list with new data that we've been given
    portalData['values'] = map(lambda x: {'value': x['snippet']['title'], 'key': x['id']}, cats)
    logging.debug("New category list: {0}".format(str(portalData['values'])))

    #step 4 - re-encode the data to get a new field record document
    portalDataNode.text = json.dumps(portalData)
    newFieldRecord = ET.tostring(xmlData,encoding="UTF-8")

    logging.debug("New field data record: {0}".format(newFieldRecord))

    #step 5 - output back to Vidispine
    (content,headers)=make_vidispine_request(h,"PUT",uri,newFieldRecord,{'Accept': 'application/xml'},content_type='application/xml')

    if int(headers['code']) < 200 or int(headers['code']) > 299:
        raise VidispineError(content)


@shared_task
def update_categories_list():
    from models import settings as plugin_settings

    #if any settings are not set, then this should raise an exception that can be caught by Raven
    logging.info("Attempting to update YouTube categories list")
    clientID = plugin_settings.objects.get(key='clientID').value
    privateKey = plugin_settings.objects.get(key='privateKey').value
    fieldName = plugin_settings.objects.get(key='fieldID').value
    try:
        regionCode = plugin_settings.objects.get(key='regionCode').value
    except plugin_settings.DoesNotExist:
        regionCode = 'gb'

    logging.info("Connecting to YouTube with clientID {0}".format(clientID))

    i = YoutubeInterface()
    i.authorize_pki(clientID,privateKey)

    logging.info("Requesting category list for region {0}".format(regionCode))
    data = i.list_categories(region_code=regionCode)

    update_vidispine_field_values(fieldName,data['items'])