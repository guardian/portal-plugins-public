from celery import shared_task
from celery.decorators import periodic_task
from celery.schedules import crontab
from django.conf import settings
import re
import logging
from datetime import datetime, timedelta
from django.db.models import Q
from time import time

logger = logging.getLogger(__name__)
id_validator = re.compile(r'^\w{2}-\d+$')


@shared_task
def calculate_project_size(project_id=None):
    """
    celery task to calculate the size of a single project
    :param project_id:
    :return:
    """
    import traceback
    from models import ProjectScanReceipt
    if project_id is not None and not id_validator.match(project_id):
        raise ValueError("{0} is not a valid vidispine id".format(project_id))

    from projectsizer import update_project_size
    if project_id is not None:
        receipt = ProjectScanReceipt.objects.get(project_id=project_id)
        receipt.last_scan = datetime.now()
        receipt.save()
    start_time = time()
    #project ID of None=>unattached
    last_error = ""
    try:
        result = update_project_size(project_id)
        logger.info("{0}: Project size information: {1}".format(project_id, result.storage_sum))
        result.save(project_id=project_id)
    except Exception as e:
        last_error = traceback.format_exc()
        logger.error(last_error)

    if project_id is not None:
        receipt = ProjectScanReceipt.objects.get(project_id=project_id)
        receipt.last_scan = datetime.now()
        receipt.last_scan_duration = time() - start_time
        receipt.last_scan_error = last_error
        receipt.save()

    logger.info("Done")


@periodic_task(run_every=crontab(hour='21',minute='03'))
def scan_all_projects():
    """
    celery task to update receipts for all projects, ensuring that we have a record of every project
    :return:
    """
    from projectscanner import ProjectScanner
    #ensure that new items get scanned by setting their last scan time to this.
    needs_scan_time = datetime.now() - timedelta(days=30)

    s = ProjectScanner()
    for projectinfo in s.scan_all():
        projectinfo.save_receipt(needs_scan_time)


@periodic_task(run_every=timedelta(minutes=30))
def launch_project_sizing():
    """
    celery task to launch the scanning of projects.
    A maximum of GNMPLUTOSTATS_PROJECT_SCAN_LIMIT are triggered at once (default 10); "In production" are highest priority,
    if none of these are applicable then "New", if none of these are applicable then everything else.
    If GNMPLUTOSTATS_PROJECT_SCAN_ENABLED is not present or False, then no scan is run
    "In Production" projects are scanned at most once a day, "New" are scanned
    at most once a day and everything else is scanned at most once a week.
    The calculate_project_size task is queued on the queue given by GNMPLUTOSTATS_PROJECT_SCAN_QUEUE (default 'celery')
    :return:
    """
    from queries import IN_PRODUCTION_NEED_SCAN, NEW_NEED_SCAN, OTHER_NEED_SCAN
    if not getattr(settings,"GNMPLUTOSTATS_PROJECT_SCAN_ENABLED",False):
        logger.error("GNMPLUTOSTATS_PROJECT_SCAN_ENABLED is false, not going to trigger launching")
        return "GNMPLUTOSTATS_PROJECT_SCAN_ENABLED is false, not going to trigger launching"

    prioritise_old = getattr(settings,"GNMPLUTOSTATS_PRIORITISE_OLD",False)
    if prioritise_old:
        logger.warning("GNMPLUTOSTATS_PRIORITISE_OLD is set, will only focus on old projects")

    trigger_limit = int(getattr(settings,"GNMPLUTOSTATS_PROJECT_SCAN_LIMIT",10))
    to_trigger = []
    c=0

    logger.info("Gathering projects to measure")

    if not prioritise_old:
        highest_priority = IN_PRODUCTION_NEED_SCAN.order_by('last_scan')
        for entry in highest_priority:
            to_trigger.append(entry)
            logger.info("{0}: {1} ({2})".format(c, entry,entry.project_status))
            c+=1
            if c>=trigger_limit:
                break

    if not prioritise_old and len(to_trigger)<trigger_limit:
        next_priority = NEW_NEED_SCAN.order_by('last_scan')
        for entry in next_priority:
            to_trigger.append(entry)
            logger.info("{0}: {1} ({2})".format(c, entry,entry.project_status))
            c+=1
            if c>=trigger_limit:
                break

    if len(to_trigger)<trigger_limit:
        everything_else = OTHER_NEED_SCAN.order_by('last_scan')
        for entry in everything_else:
            to_trigger.append(entry)
            logger.info("{0}: {1} ({2})".format(c, entry,entry.project_status))
            c+=1
            if c>=trigger_limit:
                break

    logger.info("Projects to scan: ".format(to_trigger))
    if len(to_trigger)==0:
        if prioritise_old:
            logger.error("No projects to scan and GNMPLUTOSTATS_PRIORITISE_OLD is set.  You should disable this now to pick up new projects")
        logger.info("No projects need to be scanned right now")

    n=0
    for entry in to_trigger:
        n+=1
        calculate_project_size.apply_async(kwargs={'project_id': entry.project_id},queue=getattr(settings,"GNMPLUTOSTATS_PROJECT_SCAN_QUEUE","celery"))
    return "Triggered {0} projects to scan".format(n)


@shared_task
def scan_category(category_name=""):
    """
    scans the given category and aggregate by attached/unattached (to a collection)
    :param category_name: category name to scan
    :return:
    """
    import traceback
    from categoryscanner import update_category_size_parallel
    try:
        logger.info("Starting parallel scan of category {0}".format(category_name))
        result = update_category_size_parallel(category_name)
        logger.info("Parallel scan initiated for {0}, now await results".format(category_name))
    except Exception as e:
        logger.error(traceback.format_exc())
        raise #re-raise to see error in Celery Flower


@shared_task
def scan_category_page_parallel(step_id=0):
    """
    scans a page of category results, as given by a ParallelScanStep model
    :param step_id: primary key of ParallelScanStep
    :return: Descriptive string
    """
    from models import ParallelScanStep
    import traceback
    from categoryscanner import process_next_page, ProcessResultCategory
    start_time = time()
    s = ParallelScanStep.objects.get(pk=step_id)
    s.status = "RUNNING"
    s.save()

    try:
        result = {
            'attached': ProcessResultCategory(),
            'unattached': ProcessResultCategory()
        }
        #grab the page of results
        s.retry_count = s.retry_count + 1
        result, more_pages = process_next_page(s.search_param,result,s.start_at,s.end_at-s.start_at)

        s.result = "[" + result['attached'].to_json(category_name=s.search_param,is_attached=True) + "," + result['unattached'].to_json(category_name=s.search_param,is_attached=False) + "]"
        s.status = "COMPLETED"
        s.took = time() - start_time
        s.last_error = None
        s.save()
        check_parallel_scan_completed(s.master_job.pk)
        return "Completed page scan in {0} seconds".format(s.took)
    except Exception as e:
        logger.error(traceback.format_exc())
        s.status="FAILED"
        s.took = time() - start_time
        s.last_error = traceback.format_exc()
        s.result = None
        # scan_category_page_parallel.apply_async(kwargs={"step_id": step_id},
        #                                         queue=getattr(settings,"GNMPLUTOSTATS_PROJECT_SCAN_QUEUE","celery"),
        #                                         countdown=min(3600, 2**s.retry_count))  #exponential backoff, maximum of 1 hour between runs
        s.save()
        raise


@shared_task
def check_parallel_scan_completed(scan_id=0):
    """
    checks whether all steps of a parallel scan job have completed, and updates the record if so
    :param scan_id:
    :return:
    """
    from models import ParallelScanJob, ParallelScanStep
    from categoryscanner import sum_steps
    j = ParallelScanJob.objects.get(pk=scan_id)
    if j.status!='RUNNING' and j.status!='WAITING':
        return False

    steps_total = ParallelScanStep.objects.filter(master_job=j).count()
    if steps_total==0:
        logger.error("ParallelScanJob {0} has no steps found!".format(scan_id))
        j.status = "FAILED"
        j.last_error = "ParallelScanJob {0} has no steps found!".format(scan_id)
        j.save()
        return False
    elif steps_total!=j.pages:
        logger.error("ParallelScanJob {0} has an incorrect number of steps (found {1}, expected {2})!".format(scan_id,steps_total,j.pages))
        j.status = "FAILED"
        j.last_error = "ParallelScanJob {0} has an incorrect number of steps (found {1}, expected {2})!".format(scan_id,steps_total,j.pages)
        j.save()
        return False

    steps_completed = ParallelScanStep.objects.filter(master_job=j,status='COMPLETED').count()
    steps_failed = ParallelScanStep.objects.filter(master_job=j,status='FAILED').count()
    if steps_completed==steps_total:
        logger.info("ParallelScanJob {0} completed successfully".format(scan_id))
        final_result = sum_steps(ParallelScanStep.objects.filter(master_job=j,status='COMPLETED'))
        logger.info("ParallelScanJob {0}: final result {1}".format(scan_id, final_result))
        final_result.save()
        j.status="COMPLETED"
        j.result = final_result.to_json()
        j.save()
        return True
    elif steps_completed+steps_failed==steps_total:
        logger.warning("ParallelScanJob {0}: {1} steps have failed and are retrying".format(scan_id, steps_failed))
        return False
    else:
        logger.info("ParallelScanJob {0} has not completed yet".format(scan_id))
        return False

@periodic_task(run_every=timedelta(hours=12))
def trigger_category_sizing():
    """
    scans the entire catalogue and aggregates by attached/unattached (to a collection)
    """
    from categoryscanner import find_categories
    n=0
    logger.info("triggering category sizing for entire catalogue")
    for catname in find_categories():
        n+=1
        logger.info("Rescanning size of category {0}".format(catname))
        scan_category.apply_async(kwargs={'category_name': catname},queue=getattr(settings,"GNMPLUTOSTATS_PROJECT_SCAN_QUEUE","celery"))

    logger.info("{0} categories triggered".format(n))

