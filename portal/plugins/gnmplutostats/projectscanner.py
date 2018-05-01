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
        if isinstance(self.status, list):
            self.status = self.status[0]

    def __unicode__(self):
        return u"{0}: {1} ({2})".format(self.name, self.title, self.status)

    def _get_vs_meta(self, parent_entry, fieldname):
        """
        return the values of a vidispine metadata entry, or None
        :param parent_entry:
        :return:
        """
        for fieldnode in parent_entry.findall('{0}metadata/{0}timespan/{0}field'.format(self.xmlns)):
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

    def save_receipt(self, initial_time):
        from models import ProjectScanReceipt

        (instance, created) = ProjectScanReceipt.objects.get_or_create(project_id=self.name)
        if created:
            instance.project_status = self.status
            instance.project_title = self.title
            instance.last_scan = initial_time
            instance.save()


class ProjectScanner(object):
    from .exceptions import HttpError

    xmlns = "{http://xml.vidispine.com/schema/vidispine}"

    def __init__(self):
        pass

    def _get_entries_for(self, xmldoc):
        for node in xmldoc.findall("{0}collection".format(self.xmlns)):
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
        logger.info("start_at: {0}, limit: {1}".format(start_at, limit))
        response = requests.put("{url}:{port}/API/collection;first={start};number={limit}?content=metadata&field=gnm_project_status".format(
            url=settings.VIDISPINE_URL,
            port=settings.VIDISPINE_PORT,
            start=start_at,
            limit=limit),
            auth=HTTPBasicAuth(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD),
            data=searchdoc,headers={'Content-Type': 'application/xml', 'Accept': 'application/xml'})

        if response.status_code==200:
            xmldoc = ET.fromstring(response.text.encode('ascii','xmlcharrefreplace'))
            for entry in self._get_entries_for(xmldoc):
                logger.info(u"Got project {0}".format(unicode(entry)))
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
            logger.info("{0};{1}".format(n, previous_total))
            if n==previous_total:
                break