from celery import shared_task
import datetime
import logging

logger = logging.getLogger(__name__)

@shared_task
def get_and_upload_image(thumbdata):
    from notification_handler import VSMiniThumb
    pass
