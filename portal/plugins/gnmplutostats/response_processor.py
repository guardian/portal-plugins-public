import xml.etree.cElementTree as ET
import logging
from .exceptions import *

logger = logging.getLogger(__name__)

class ResponseProcessor(object):
    xmlns = "{http://xml.vidispine.com/schema/vidispine}"

    def __init__(self, textcontent):
        if textcontent is not None:
            try:
                self._doc = ET.fromstring(textcontent.encode('ascii','xmlcharrefreplace'))
            except UnicodeDecodeError as e:
                logger.warning(e)
                self._doc = ET.fromstring(textcontent.decode('utf-8','xmlcharrefreplace').encode('ascii','xmlcharrefreplace'))

    @property
    def total_hits(self):
        """
        total number of items matching the query as provided by Vidispine
        :return:
        """
        return int(self._doc.find("{0}hits".format(self.xmlns)).text)

    @property
    def entries(self):
        """
        number of entries in this batch
        :return:
        """
        return len(self._doc.findall("{0}item".format(self.xmlns)))

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

    @staticmethod
    def get_right_component(item_entry):
        """
        returns the right component for the "main" content
        :param item_entry:
        :return:
        """
        possible_components = [
            "{0}containerComponent".format(ResponseProcessor.xmlns),
            "{0}binaryComponent".format(ResponseProcessor.xmlns),
        ]

        for c in possible_components:
            if item_entry.find(c) is not None:
                return c
        return None

    def item_size(self, item_entry, process_result, shape_tag="original"):
        """
        get the total size of files of the given shape tag for the given item
        :param item_entry: pointer to an <item> node in the returned document
        :param process_result: ProcessResult instance to update
        :param shape_tag: shape tag to get
        :return:
        """
        item_id = item_entry.attrib['id']
        n=0
        for shape_entry in item_entry.findall("{0}shape".format(self.xmlns)):
            entry_shape_tag = self._get_xml_entry(shape_entry, "{0}tag".format(self.xmlns))
            if entry_shape_tag!=shape_tag:
                logger.debug("shape had incorrect tag {0} (wanted {1})".format(entry_shape_tag, shape_tag))
                continue
            component_name = self.get_right_component(shape_entry)
            if component_name is None:
                logger.warning("Original content: {0}".format(ET.tostring(shape_entry)))
                raise RuntimeError("Could not determine the right content type to use")

            n+=1

            try:
                logger.info("Got {0} for storage {1}".format(
                    self._get_xml_entry(shape_entry,"{1}/{0}file/{0}size".format(self.xmlns, component_name)),
                    self._get_xml_entry(shape_entry,"{1}/{0}file/{0}storage".format(self.xmlns, component_name))
                ))

                process_result.add_entry(self._get_xml_entry(shape_entry,"{1}/{0}file/{0}storage".format(self.xmlns, component_name)),
                                         self._get_xml_entry(shape_entry,"{1}/{0}file/{0}size".format(self.xmlns, component_name)))
            except TypeError as e:
                logger.warning("Original content: {0}".format(ET.tostring(shape_entry)))
                logger.warning("Value {0} for {1} does not seem to be a number (can't convert to float)"
                               .format(self._get_xml_entry(shape_entry,"{1}/{0}file/{0}size".format(self.xmlns, component_name)),
                                       self._get_xml_entry(shape_entry,"{1}/{0}file/{0}path".format(self.xmlns, component_name)))
                               )
        if n==0:
            logger.warning("Item {0}: No shape entries could be found".format(item_id))

    def page_size(self, process_result,shape_tag="original"):
        """
        get the total size of files of the given shape tag in this page of results
        :param process_result: ProcessResult instance to update
        :param shape_tag: shape tag to get
        :return:
        """
        for item_entry in self._doc.findall("{0}item".format(self.xmlns)):
            self.item_size(item_entry, process_result, shape_tag)

    def get_item_metadata_field(self, item_node, mdfield):
        for fieldnode in item_node.findall('{0}metadata/{0}timespan/{0}field'.format(self.xmlns)):
            namenode = fieldnode.find('{0}name'.format(self.xmlns))
            if namenode is None: continue
            if namenode.text==mdfield:
                return fieldnode.find('{0}value'.format(self.xmlns)).text
        raise InvalidMetadata("No {0} field could be found".format(mdfield))

    def page_size_split_attach(self, process_result_attached, process_result_unattached, shape_tag="original"):
        """
        get the total size of files of the given shape tag in this page of results, split into ones that are attached to
        a collection and not attached to any collection
        :param process_result_attached: ProcessResult instance to update if an item is attached
        :param process_result_unattached: ProcessResult instance to update if an item is not attached
        :param shape_tag: shape tag to get
        :return:
        """
        for item_entry in self._doc.findall("{0}item".format(self.xmlns)):
            collection_size = int(self.get_item_metadata_field(item_entry, "__collection_size"))
            if collection_size>0:
                self.item_size(item_entry, process_result_attached, shape_tag=shape_tag)
            else:
                self.item_size(item_entry, process_result_unattached, shape_tag=shape_tag)