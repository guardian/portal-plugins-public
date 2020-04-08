import requests
from django.conf import settings
from xml.etree.cElementTree import fromstring
import logging

logger = logging.getLogger(__name__)

xmlns = "{http://xml.vidispine.com/schema/vidispine}"


def list_shape_ids(vsid):
    url = "{0}:{1}/API/item/{2}/shape".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,vsid)
    result = requests.get(url, auth=(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD), headers={"Accept":"application/xml"})
    if result.status_code == 200:
        doc = fromstring(result.text.encode("utf-8"))
        for node in doc.findall("{0}uri".format(xmlns)):
            yield node.text
    else:
        raise StandardError("could not list shape ids on {0}, server returned {1}".format(vsid, result.status_code))


def check_shape_tag(vsid, shapeid, tagtofind):
    """
    check if the given shape on the given item is of the given shape tag
    if it is, then return the parsed document tree
    :param vsid:  vidispine item ID
    :param shapeid:  shape ID on the item ID
    :param tagtofind: shape tagname
    :return: either None or the parsed xml data
    """
    url = "{0}:{1}/API/item/{2}/shape/{3}".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,vsid, shapeid)
    result = requests.get(url, auth=(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD), headers={"Accept":"application/xml"})
    if result.status_code == 200:
        doc = fromstring(result.text.encode("utf-8"))
        shape_tag_node = doc.find("{0}tag".format(xmlns))

        if shape_tag_node is None:
            logger.warn("shape {0} on item {1} has no shape tag node".format(shapeid, vsid))
            return None

        if shape_tag_node.text == tagtofind:
            return doc
        else:
            return None
    else:
        raise StandardError("could not list shape ids on {0}, server returned {1}".format(vsid, result.status_code))


def check_for_broken_proxy(vsid):
    """
    check whether the given item id has a "broken" proxy, i.e. a lowres shape on it with no data.
    a valid shape should have a "containerComponent" on it.
    if there is no lowres shape present, then True is also returned
    :param vsid:
    :return: a boolean indicating whether the proxy should be regenrated and the shape ID of the proxy or None
    """
    for shape_id in list_shape_ids(vsid):
        shapeinfo = check_shape_tag(vsid, shape_id, "lowres")
        if shapeinfo is not None:
            #we have the lowres shape
            container_component_node = shapeinfo.find("{0}containerComponent".format(xmlns))
            if container_component_node is None:
                logger.warning("{0}: item has an invalid proxy".format(vsid))
                return True, shape_id
            else:
                logger.info("{0}: item has a valid proxy".format(vsid))
                return False, shape_id

    logger.error("{0}: item has no proxy at all!".format(vsid))
    return True, None


def delete_existing_proxy(vsid, shape_id):
    """
    sends a DELETE request to vidispine for the given shape on the given item
    :param vsid:
    :param shape_id:
    :return:
    """
    url = "{0}:{1}/API/item/{2}/shape/{3}".format(settings.VIDISPINE_URL, settings.VIDISPINE_PORT, vsid, shape_id)
    response = requests.delete(url, auth=(settings.VIDISPINE_USERNAME, settings.VIDISPINE_PASSWORD))
    if 299 > response.status_code >= 200:
       return True
    else:
        raise StandardError("could not delete shape {0} on {1}, server returned {2}".format(shape_id, vsid, response.status_code))


def transcode_proxy(vsid, shape_tag):
    """
    requests that vidispine create a new proxy of the given tag
    :param vsid: item to proxy
    :param shape_tag: type of proxy to create
    :return:
    """
    url = "{0}:{1}/API/item/{2}/transcode?priority=HIGH&tag={3}".format(settings.VIDISPINE_URL, settings.VIDISPINE_PORT, vsid, shape_tag)
    response = requests.post(url, auth=(settings.VIDISPINE_USERNAME, settings.VIDISPINE_PASSWORD))
    if 299 > response.status_code >= 200:
        logger.info("{0}: transcode started successfully: {1}".format(vsid, response.text))
        return True
    else:
        raise StandardError("could not transcode shape {0} on {1}, server returned {2}".format(shape_tag, vsid, response.status_code))