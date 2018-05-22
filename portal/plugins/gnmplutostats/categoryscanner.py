import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
import logging
from response_processor import ResponseProcessor
from datetime import datetime
from process_result import ProcessResult
from .exceptions import HttpError
from time import sleep
import xml.etree.cElementTree as ET

logger = logging.getLogger(__name__)


class ProcessResultCategory(ProcessResult):
    def save(self,**kwargs):
        """
        saves the contents of the ProcessResult to a series of data model entries, one for each storage
        :param category_name: category name to save against
        :param is_attached: boolean indicating whether this data is for attached or unattached items
        :return: the number of rows saved
        """
        from models import CategoryScanInfo
        category_name=kwargs['category_name']
        is_attached=kwargs['is_attached']
        n=0
        for storage_id,total_size in self.storage_sum.items():
            if total_size is None:
                continue
            (record, created) = CategoryScanInfo.objects.get_or_create(category_label=category_name,attached=is_attached,
                                                                      storage_id=storage_id,
                                                                      defaults={"size_used_gb": total_size,"last_updated": datetime.now()})
            record.size_used_gb = total_size
            record.last_updated = datetime.now()
            record.save()
            n+=1
        return n


def find_categories():
    """
    returns a list of values for gnm_asset_category
    :return:
    """
    searchdoc = """<ItemSearchDocument xmlns="http://xml.vidispine.com/schema/vidispine">
	<facet count="true">
		<field>gnm_asset_category</field>
	</facet>
</ItemSearchDocument>"""
    xmlns="{http://xml.vidispine.com/schema/vidispine}"

    response = requests.put("{url}:{port}/API/item;number=0?".format(
        url=settings.VIDISPINE_URL,
        port=settings.VIDISPINE_PORT),
        auth=HTTPBasicAuth(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD),
        data=searchdoc,headers={'Content-Type': 'application/xml', 'Accept': 'application/xml'})

    if response.status_code==200:
        doc = ET.fromstring(response.text)
        return map(lambda countnode: countnode.attrib['fieldValue'], doc.findall('{0}facet/{0}count'.format(xmlns)))
    else:
        raise HttpError(response)


def process_next_page(category_name, process_result_dict, start_at, limit):
    """
    grabs another page of search results and processes them
    :param category_name: category name to scan
    :param process_result_dict: dict of ProcessResult objects representing attached and unattached items to update
    :param start_at: item number to start at (first item is 1)
    :param limit: page size
    :return: tuple of (process_result, more_pages)
    """
    searchdoc = """<ItemSearchDocument xmlns="http://xml.vidispine.com/schema/vidispine">
    <field>
        <name>gnm_asset_category</name>
        <value>{0}</value>
    </field>
</ItemSearchDocument>""".format(category_name)

    process_result_attached = process_result_dict['attached']
    process_result_unattached = process_result_dict['unattached']

    response = requests.put("{url}:{port}/API/item;first={start};number={limit}?content=shape,metadata&field=__collection_size".format(
        url=settings.VIDISPINE_URL,
        port=settings.VIDISPINE_PORT,
        start=start_at,
        limit=limit),
        auth=HTTPBasicAuth(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD),
        data=searchdoc,headers={'Content-Type': 'application/xml', 'Accept': 'application/xml'})

    if response.status_code==200:
        xmldoc = ResponseProcessor(response.text)
        logger.info("{0}: Got page with {1}/{2} items".format(category_name, xmldoc.entries, xmldoc.total_hits))
        if xmldoc.entries==0:
            logger.info("{0}: all items from category counted".format(category_name))
            return ({'attached': process_result_attached, 'unattached': process_result_unattached}, False)
        xmldoc.page_size_split_attach(process_result_attached, process_result_unattached)
        logger.info("{0}: Running total is {1} attached, {2} unattached".format(category_name, process_result_attached, process_result_unattached))
        return ({'attached': process_result_attached, 'unattached': process_result_unattached}, True)
    else:
        raise HttpError(response)


def update_category_size(category_name):
    """
    scans the project at project_id and returns a ProcessResult object containing the final data
    :param category_name: category to scan
    :return: ProcessResult object
    """
    page_size = 40
    page_start=1
    retry_limit=5
    retry_count=0
    result = {
        'attached': ProcessResultCategory(),
        'unattached': ProcessResultCategory()
    }

    more_pages = True
    while more_pages:
        try:
            logger.info("{0}: Getting page for items {1} to {2}...".format(category_name,page_start, page_start+page_size))
            (result, more_pages) = process_next_page(category_name, result, start_at=page_start, limit=page_size)
            page_start+=page_size+1
        except HttpError as e:
            logger.error(str(e))
            retry_count+=1
            if retry_count>=retry_limit:
                logger.error("Retried {0} times already, aborting".format(retry_count))
                raise
            if e.status_code>=400 and e.status_code<=500:
                logger.error("Not retrying")
                raise
            logger.info("Retrying after 10s delay")
            sleep(10)
    logger.info("{0}: Completed".format(category_name))
    return result
