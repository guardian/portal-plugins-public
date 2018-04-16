import requests
import logging
import hashlib
import hmac
from datetime import datetime
import base64
import requests
from time import mktime
from urlparse import urlparse
from pprint import pformat

logger = logging.getLogger(__name__)


class HttpError(StandardError):
    def __init__(self, uri, code, content, sent_headers, response_headers):
        self.code = code
        self.uri = uri
        self.content = content
        self.request_headers = sent_headers
        self.response_headers = response_headers

    def __str__(self):
        return "HTTP error {code} accessing {uri}".format(code=self.code, uri=self.uri)


def get_token(uri, secret, override_time=None):
    from email.utils import formatdate

    if override_time:
        dt = override_time
    else:
        dt = datetime.now()
    httpdate = formatdate(timeval=mktime(dt.timetuple()),localtime=False,usegmt=True)
    url_parts = urlparse(uri)

    string_to_sign = "{0}\n{1}".format(httpdate, url_parts.path)
    logger.debug("string_to_sign: " + string_to_sign)
    hm = hmac.new(secret, string_to_sign,hashlib.sha256)
    return "HMAC {0}".format(base64.b64encode(hm.digest())), httpdate


def request_atom_resend(atomid, host, secret):
    """
    Message the media atom tool to request that the atom is resynced
    :param options:
    :return:
    """
    uri = "https://{host}/api2/pluto/resend/{id}".format(host=host, id=atomid)
    logger.debug("uri is " + uri)
    authtoken, httpdate = get_token(uri, secret)
    logger.debug(authtoken)

    headers = {
        'X-Gu-Tools-HMAC-Date': httpdate,
        'X-Gu-Tools-HMAC-Token': authtoken
    }

    logger.debug(headers)
    response = requests.post(uri,headers=headers)
    logger.debug("Server returned {0}".format(response.status_code))
    logger.debug(pformat(response.headers))
    if response.status_code==200:
        logger.debug(pformat(response.json()))
    else:
        raise HttpError(uri,response.status_code, response.text, headers, response.headers)
