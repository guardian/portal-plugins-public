import requests
from vsmixin import HttpError
from requests.auth import HTTPBasicAuth
import xml.etree.cElementTree as ET
from django.conf import settings
import logging
from time import sleep
import dateutil.parser
from uuid import UUID
logger = logging.getLogger(__name__)


class ProjectHistoryChange(object):
    def __init__(self, fieldname, uuid, timestamp, user, newvalue):
        self.fieldname = fieldname
        self.uuid = UUID(uuid)
        self.timestamp = dateutil.parser.parse(timestamp)
        self.user = user
        self.newvalue = newvalue

    def __eq__(self, other):
        return other.fieldname==self.fieldname and other.uuid==self.uuid and other.timestamp==self.timestamp and other.user==self.user and other.newvalue==self.newvalue

    def __str__(self):
        return "{0}: {1} changed {2} to {3}".format(self.timestamp, self.user, self.fieldname, self.newvalue)


class ProjectHistory(object):
    xmlns = "{http://xml.vidispine.com/schema/vidispine}"

    def __init__(self, project_id, interesting_fields=["gnm_project_status","title"], load_now=True):
        self.project_id = project_id
        self.interesting_fields = interesting_fields
        self.changes = []
        if load_now: self.update()

    def changes_for_field(self, field_name):
        return filter(lambda changeEntry: changeEntry.fieldname==field_name,self.changes)

    def _process_changeset_timespan_field(self,fieldNode,ts_start,ts_end):
        nameNode = fieldNode.find('{0}name'.format(self.xmlns))
        if nameNode is None: return None

        field_name = nameNode.text
        if not field_name in self.interesting_fields: return None

        return map(lambda valueNode: ProjectHistoryChange(field_name, valueNode.attrib['uuid'], valueNode.attrib['timestamp'], valueNode.attrib['user'], valueNode.text), fieldNode.findall('{0}value'.format(self.xmlns)))

    def _process_changeset_timespan(self, timespanNode):
        ts_start = timespanNode.attrib['start']
        ts_end = timespanNode.attrib['end']
        field_updates = map(lambda fieldNode: self._process_changeset_timespan_field(fieldNode, ts_start, ts_end), timespanNode.findall('{0}field'.format(self.xmlns)))
        return filter(lambda change: change is not None, field_updates)

    def _process_changeset(self, changeSetNode):
        """
        extracts useful information from a changeset node
        :param changeSetNode:
        :return:
        """
        return map(lambda timespanNode: self._process_changeset_timespan(timespanNode), changeSetNode.findall('{0}metadata/{0}timespan'.format(self.xmlns)))

    def _flatten_array(self, lists):
        rtn = []
        for item in lists:
            if item is None:
                continue
            elif isinstance(item,list):
                new_list = self._flatten_array(item)
                if new_list is not None and len(new_list)>0:
                    rtn = rtn + new_list
            else:
                rtn.append(item)
        return rtn

    def _process_xml_doc(self, xmldoc):
        changes = self._flatten_array(map(lambda changeSetNode: self._process_changeset(changeSetNode), xmldoc.findall('{0}changeSet'.format(self.xmlns))))
        return changes

    def update(self, max_retries=20, retry_delay=1):
        """
        updates this object from the system data
        :return:
        """
        attempts=0
        while True:
            attempts+=1
            md_url = "{0}:{1}/API/collection/{2}/metadata/changes".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,self.project_id)
            result = requests.get(url=md_url,
                                  auth=HTTPBasicAuth(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD),
                                  headers={'Accept': 'application/xml'})
            if result.status_code==200:
                break
            logger.error("{0}/{1}: Could not communicate with vidispine: {2} {3}".format(attempts,max_retries,result.status_code, result.text))
            if attempts>=max_retries:
                raise HttpError(md_url,"GET","",result.headers,result.content)
            sleep(retry_delay)

        xmldoc = ET.fromstring(result.text)
        self.changes = self._process_xml_doc(xmldoc)