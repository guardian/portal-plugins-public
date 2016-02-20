from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def complete_project_setup(commission_id,project_id,user_id):
    from portal.plugins.gnm_notifications.models import send_notification
    from django.core.urlresolvers import reverse, reverse_lazy
    from portal.plugins.gnm_notifications.choices import NOTIFICATION_TYPE_PROJECT, NOTIFICATION_SEVERITY_INFO
    from portal.plugins.gnm_vidispine_utils import constants as const
    from portal.plugins.gnm_projects.models import VSProject
    from portal.plugins.gnm_commissions.models import VSCommission
    from portal.plugins.gnm_commissions.exceptions import NotACommissionError

    commission = VSCommission(commission_id, user_id)
    project = VSProject(project_id, user_id)

    commission.add_project(project)

    send_notification(
        type=NOTIFICATION_TYPE_PROJECT,
        severity=NOTIFICATION_SEVERITY_INFO,
        to=project.subscribers(),
        object_type='Project',
        object_id=project.id,
        message=u'Project created: {title}'.format(title=project.get(const.GNM_PROJECT_HEADLINE, '')),
        url=reverse('project', args=[project.id]))
