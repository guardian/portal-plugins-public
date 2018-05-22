import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
import logging
from time import sleep
from datetime import datetime
from .exceptions import HttpError
from response_processor import ResponseProcessor
from process_result import ProcessResult
logger = logging.getLogger(__name__)


class ProcessResultProject(ProcessResult):
    def save(self, project_id):
        from models import ProjectSizeInfoModel
        from datetime import datetime
        n=0
        for storage_id,total_size in self.storage_sum.items():
            if total_size is None:
                continue
            (record, created) = ProjectSizeInfoModel.objects.get_or_create(project_id=project_id,
                                                                           storage_id=storage_id,
                                                                           defaults={"size_used_gb": total_size,"last_updated": datetime.now()})
            record.size_used_gb = total_size
            record.last_updated = datetime.now()
            record.save()
            n+=1
        return n


def process_next_page(project_id, process_result, start_at, limit, unattached=False):
    """
    grabs another page of search results and processes them
    :param project_id: project id to search
    :param process_result: ProcessResult object to update
    :param start_at: item number to start at (first item is 1)
    :param limit: page size
    :return: tuple of (process_result, more_pages)
    """
    if project_id is None:
        searchdoc = """<ItemSearchDocument xmlns="http://xml.vidispine.com/schema/vidispine">
	<operator operation="NOT"><field>
		<name>__collection</name>
		<value>*</value>
	</field></operator>
</ItemSearchDocument>"""
    else:
        searchdoc = """<ItemSearchDocument xmlns="http://xml.vidispine.com/schema/vidispine">
        <field>
            <name>__collection</name>
            <value>{0}</value>
        </field>
    </ItemSearchDocument>""".format(project_id)

    response = requests.put("{url}:{port}/API/item;first={start};number={limit}?content=shape".format(
                                url=settings.VIDISPINE_URL,
                                port=settings.VIDISPINE_PORT,
                                start=start_at,
                                limit=limit),
                            auth=HTTPBasicAuth(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD),
                            data=searchdoc,headers={'Content-Type': 'application/xml', 'Accept': 'application/xml'})

    if response.status_code==200:
        xmldoc = ResponseProcessor(response.text)
        logger.info("{0}: Got page with {1}/{2} items".format(project_id, xmldoc.entries, xmldoc.total_hits))
        if xmldoc.entries==0:
            logger.info("{0}: all items from project counted".format(project_id))
            return (process_result, False)
        xmldoc.page_size(process_result)
        logger.info("{0}: Running total is {1}".format(project_id, process_result))
        return (process_result, True)
    else:
        raise HttpError(response)


def update_project_size(project_id):
    """
    scans the project at project_id and returns a ProcessResult object containing the final data
    :param project_id: project to scan
    :return: ProcessResult object
    """
    page_size = 40
    page_start=1
    retry_limit=5
    retry_count=0
    result = ProcessResultProject()

    more_pages = True
    while more_pages:
        try:
            logger.info("{0}: Getting page for items {1} to {2}...".format(project_id,page_start, page_start+page_size))
            (result, more_pages) = process_next_page(project_id, result, start_at=page_start, limit=page_size)
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
    logger.info("{0}: Completed".format(project_id))
    return result
