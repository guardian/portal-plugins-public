from celery.signals import task_failure,task_success,task_revoked
import logging
from django.dispatch import receiver
import os

if not 'CI' in os.environ:
    #this import at root level makes things tricky, but is necessary to support the sender= argument on the decorators
    #below.
    from portal.plugins.gnm_masters.tasks import update_pacdata
else:
    #dummy implementation for CI
    def update_pacdata():
        pass

logger = logging.getLogger(__name__)

logger.info("registering signal handlers")

@receiver(task_success, sender=update_pacdata)
def edl_import_success(signal=None,result=None,sender=None,**kwargs):
    #sender is of type Task
    from models import PacFormXml
    taskid = sender.request.id
    logger.info("update edl data task {0} ({1}) completed with {2}".format(taskid, sender.name, result))

    try:
        pac_xml_task = PacFormXml.objects.get(celery_task_id=taskid)
        pac_xml_task.status = "PROCESSED"
        pac_xml_task.last_error = ""
        pac_xml_task.save()
        logger.info("Updated pac form xml information")
    except PacFormXml.DoesNotExist:
        logger.warning("PAC form import completed on something not imported from atom tool")
    except Exception as e:
        logger.exception(str(e))


@receiver(task_failure, sender=update_pacdata)
def edl_import_failure(task_id=None,exception=None, traceback=None, sender=None, **kwargs):
    logger.info("edl_import_failure: {0}".format(kwargs))
    logger.warning("update edl data task {0} ({2}) failed with {1}".format(task_id, unicode(exception), sender.name))
    from models import PacFormXml

    try:
        pac_xml_task = PacFormXml.objects.get(celery_task_id=task_id)
        pac_xml_task.status = "ERROR"
        pac_xml_task.last_error = traceback.format_exc()
        pac_xml_task.save()
        logger.info("Updated pac form xml information for failed task")
    except PacFormXml.DoesNotExist:
        logger.warning("PAC form import failed on something not imported from atom tool")
    except Exception as e:
        logger.exception(str(e))


@task_revoked.connect()#(sender='portal.plugins.gnm_masters.edl_import.update_edl_data')
def edl_import_revoked(request=None, signum=None, terminated=None, expired=None, sender=None, **kwargs):
    from models import PacFormXml
    taskid = sender.request.id

    logger.warning("PAC form import task {0} revoked".format(taskid))
    if taskid is None:
        return #can't do anything if we have not had a task id passed
    try:
        pac_xml_task = PacFormXml.objects.get(celery_task_id=taskid)
        pac_xml_task.status = "ERROR"
        pac_xml_task.last_error = """Task revoked on signal number {0}\nTerminated? {1}\nExpired? {2}""".format(signum, terminated, expired)
        pac_xml_task.save()
        logger.info("Updated pac form xml information for revoked task")
    except PacFormXml.DoesNotExist:
        logger.warning("PAC form import revoked on something not imported from atom tool")
    except Exception as e:
        logger.exception(str(e))