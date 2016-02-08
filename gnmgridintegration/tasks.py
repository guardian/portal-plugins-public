from celery import shared_task
import datetime
import logging

logger = logging.getLogger(__name__)

@shared_task
def get_and_upload_image(thumbdata):
    from notification_handler import VSMiniThumb
    from grid_api import GridLoader
    from django.conf import settings

    loader = GridLoader('pluto_gnmgridintegration',settings.GNM_GRID_API_KEY)
    pass

