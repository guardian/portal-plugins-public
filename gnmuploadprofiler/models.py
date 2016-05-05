from django.db import models
from django.utils import html
import logging

logger = logging.getLogger(__name__)


class OutputTimings(models.Model):
    item_id = models.CharField(max_length=255,unique=True,db_index=True)
    item_duration = models.FloatField(default=0.0)
    created_time = models.DateTimeField()
    proxy_completed_interval = models.FloatField(blank=True,default=0.0)
    upload_trigger_interval = models.FloatField(blank=True,default=0.0)
    page_created_interval = models.FloatField(blank=True,default=0.0)
    final_transcode_completed_interval = models.FloatField(blank=True,default=0.0)
    page_launch_guess_interval = models.FloatField(blank=True,default=0.0)
    completed_time = models.DateTimeField(blank=True)

    class Meta:
        ordering = ['-completed_time','-created_time']