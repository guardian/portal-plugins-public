from celery import shared_task
from django.conf import settings


@shared_task
def create_link_for(item_id, shape_tag):
    """
    Task to trigger the optional transcoding and upload of an item
    :param item_id:
    :return:
    """
    from gnmvidispine.vs_item import VSItem
    from gnmvidispine.vs_job import VSJob
    pass
