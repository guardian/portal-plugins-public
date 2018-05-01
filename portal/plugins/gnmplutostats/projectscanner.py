import requests
from requests.auth import HTTPBasicAuth
import logging
from django.conf import settings
import xml.etree.cElementTree as ET
from datetime import datetime
logger = logging.getLogger(__name__)


class ProjectInfo(object):
    xmlns = "{http://xml.vidispine.com/schema/vidispine}"

    def __init__(self, xmlnode):
        self.name = self._get_xml_entry(xmlnode, "{0}id".format(self.xmlns))
        self.title = self._get_xml_entry(xmlnode,"{0}name".format(self.xmlns))
        self.status = self._get_vs_meta(xmlnode,"gnm_project_status")

    def _get_vs_meta(self, parent_entry, fieldname):
        """
        return the values of a vidispine metadata entry, or None
        :param parent_entry:
        :return:
        """
        for fieldnode in parent_entry.findall('{0}field'.format(self.xmlns)):
            if self._get_xml_entry(fieldnode,"{0}name".format(self.xmlns))==fieldname:
                return map(lambda node: node.text, fieldnode.findall('{0}value'.format(self.xmlns)))
        return None

    def _get_xml_entry(self, parent_entry, tag_name):
        """
        return the value of the given entry or None
        :param parent_entry:
        :param tag_name:
        :return:
        """
        node = parent_entry.find(tag_name)
        if node is None:
            return None
        else:
            return node.text

    def save_receipt(self):
        from models import ProjectScanReceipt

        (instance, created) = ProjectScanReceipt.objects.get_or_create(project_id=self.name)
        if created:
            instance.project_status = self.status
            instance.project_title = self.title
            instance.save()

class ProjectScanner(object):
    from .exceptions import HttpError

    xmlns = "{http://xml.vidispine.com/schema/vidispine}"

    def __init__(self):
        pass

    def _get_entries_for(self, xmldoc):
        for node in xmldoc.find("{0}collection".format(self.xmlns)):
            yield ProjectInfo(node)

    def scan_next_page(self, start_at,limit):
        """
        scans the next page of results, yields ProjectInfo objects as a generator for each piece of data found
        :param start_at:
        :param limit:
        :return:
        """
        searchdoc = """<ItemSearchDocument xmlns="http://xml.vidispine.com/schema/vidispine">
            <field>
                <name>gnm_type</name>
                <value>project</value>
            </field>
        </ItemSearchDocument>"""

        response = requests.put("{url}:{port}/API/collection;start={start};number={limit}?content=metadata&field=gnm_project_status".format(
            url=settings.VIDISPINE_URL,
            port=settings.VIDISPINE_PORT,
            start=start_at,
            limit=limit),
            auth=HTTPBasicAuth(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD),
            body=searchdoc,headers={'Content-Type': 'application/xml', 'Accept': 'application/xml'})

        if response.status_code==200:
            xmldoc = ET.fromstring(response.text)
            for entry in self._get_entries_for(xmldoc):
                yield entry
        else:
            raise self.HttpError(response)

    def scan_all(self, page_size=50):
        """
        scans for all projects in the system, yields ProjectInfo objects as a generator
        :return:
        """
        n=1
        while True:
            previous_total=n
            for entry in self.scan_next_page(n, page_size):
                n+=1
                yield entry
            if n==previous_total:
                break