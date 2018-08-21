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

MSG_PROJECT_CREATED = 'project-created'
MSG_PROJECT_UPDATED = 'project-updated'


def update_kinesis(project_model, message_type):
    """
    notifies media atom of a project update or create by pushing a message onto its kinesis stream.
    the kinesis stream is indicated in settings.
    :param project_model: ProjectModel instance that has been created/updated
    :param message_type: either `media_atom.MSG_PROJECT_CREATED` or `media_atom.MSG_PROJECT_UPDATED`
    :return:
    """
    from portal.plugins.gnm_vidispine_utils.vs_helpers import site_id
    from boto import sts, kinesis
    from django.conf import settings
    import json, logging

    SESSION_NAME = 'pluto-media-atom-integration'

    project_id = site_id + "-" + str(project_model.collection_id)
    logger.info("{0}: Project updated, notifying {1} via role {2}".format(project_id, settings.MEDIA_ATOM_STREAM_NAME, settings.MEDIA_ATOM_ROLE_ARN))

    sts_connection = sts.STSConnection(
        aws_access_key_id=settings.MEDIA_ATOM_AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.MEDIA_ATOM_AWS_SECRET_ACCESS_KEY)

    assume_role_result = sts_connection.assume_role(
        role_arn=settings.MEDIA_ATOM_ROLE_ARN,
        role_session_name=SESSION_NAME)

    credentials = assume_role_result.credentials

    logger.debug("{0}: Got kinesis credentials".format(project_id))
    kinesis_connection = kinesis.connect_to_region(
        region_name='eu-west-1',
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_key,
        security_token=credentials.session_token)

    message_content = {
        'type': message_type,
        'id': project_id,
        'title': project_model.gnm_project_headline,
        'status': project_model.gnm_project_status,
        'commissionId': site_id + str(project_model.commission.collection_id),
        'commissionTitle': project_model.commission.gnm_commission_title,
        'productionOffice': None, #this is not used to my knowlege?
        'created': project_model.created.isoformat()
    }
    logger.debug("{0}: Message is {1}".format(project_id, message_content))

    kinesis_connection.put_record(
        stream_name=settings.MEDIA_ATOM_STREAM_NAME,
        data=json.dumps(message_content),
        partition_key=project_model.collection_id)
    logger.info("{0}: Project update sent".format(project_id))