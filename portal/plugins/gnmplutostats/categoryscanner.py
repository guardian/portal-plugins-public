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
        category_name=kwargs['category_name'] if 'category_name' in kwargs else self.extra_data['category_label']
        is_attached=kwargs['is_attached'] if 'is_attached' in kwargs else self.extra_data['is_attached']

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

    @property
    def category_label(self):
        return self.extra_data['category_label']

    @property
    def is_attached(self):
        return self.extra_data['is_attached']

    @staticmethod
    def from_json(jsonstring):
        import json
        data = json.loads(jsonstring)

        result = ProcessResultCategory()
        result.storage_sum = dict(map(lambda entry: (entry['storage_id'], entry['size_used_gb'], ),data['storage_data']))

        for k,v in data.items():
            result.extra_data[k] = v
        return result

    def to_json(self,**kwargs):
        """
        returns a json representation of the data
        :return:
        """
        import json
        category_name=kwargs['category_name']
        is_attached=kwargs['is_attached']

        return json.dumps({
            'category_label': category_name,
            'attached': is_attached,
            'storage_data': map(lambda (storage_id,total_size): {"size_used_gb": total_size, "storage_id": storage_id}, self.storage_sum.items())
        })


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


def get_total_hits(category_name):
    """
    grabs another page of search results and processes them
    :param category_name: category name to scan
    :param process_result_dict: dict of ProcessResult objects representing attached and unattached items to update
    :param start_at: item number to start at (first item is 1)
    :param limit: page size
    :return: tuple of (process_result, more_pages)
    """
    from xml.sax.saxutils import escape

    searchdoc = """<ItemSearchDocument xmlns="http://xml.vidispine.com/schema/vidispine">
    <field>
        <name>gnm_asset_category</name>
        <value>{0}</value>
    </field>
</ItemSearchDocument>""".format(escape(category_name))

    response = requests.put("{url}:{port}/API/item;number=0".format(
        url=settings.VIDISPINE_URL,
        port=settings.VIDISPINE_PORT),
        auth=HTTPBasicAuth(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD),
        data=searchdoc,headers={'Content-Type': 'application/xml', 'Accept': 'application/xml'})

    if response.status_code==200:
        xmldoc = ResponseProcessor(response.text)
        logger.info("{0}: Got total hits {1}".format(category_name, xmldoc.total_hits))
        return xmldoc.total_hits
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
    from xml.sax.saxutils import escape

    searchdoc = """<ItemSearchDocument xmlns="http://xml.vidispine.com/schema/vidispine">
    <field>
        <name>gnm_asset_category</name>
        <value>{0}</value>
    </field>
</ItemSearchDocument>""".format(escape(category_name))

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
            logger.info("Retrying after 10s delay")
            sleep(10)
    logger.info("{0}: Completed".format(category_name))
    return result


def update_category_size_parallel(category_name):
    """
    triggers parallel jobs to scan each page of category results
    :param category_name: name of categories to scan
    :return: ParallelScanJob instance
    """
    from models import ParallelScanJob, ParallelScanStep
    from math import ceil
    from tasks import scan_category_page_parallel
    page_size = 40
    retry_limit=5
    retry_count=0

    while True:
        try:
            retry_count+=1
            total_hits = get_total_hits(category_name)
            break
        except HttpError as e:
            logger.warning(str(e))
            sleep(5)
            if retry_count>retry_limit:
                raise

    j = ParallelScanJob(
        job_desc="CategorySizeParallel",
        status="WAITING",
        items_to_scan=total_hits,
        pages=ceil(float(total_hits)/float(page_size))
    )
    j.save()

    for page_start in range(1,total_hits,page_size):
        s = ParallelScanStep(
            master_job=j,
            status="WAITING",
            search_param=category_name,
            start_at=page_start,
            end_at=page_start+page_size-1   #-1 required because we start from item 1. So 1st page is 1->(1+40-1) = 1->40
        )
        s.save()
        task_data = scan_category_page_parallel.apply_async(kwargs={"step_id": s.pk},
                                                            queue=getattr(settings,"GNMPLUTOSTATS_PROJECT_SCAN_QUEUE","celery"))
        s.task_id = task_data.task_id
        s.save()


def sum_steps(step_records):
    """
    aggregate the total results from all job steps
    :param step_records: iterable of job steps to sum
    :return: dictionary of aggregated results
    """
    first_record = ProcessResultCategory.from_json(step_records[0].result)

    return reduce(lambda acc,record: acc.combine(ProcessResultCategory.from_json(record.result)), step_records[1:], first_record)
