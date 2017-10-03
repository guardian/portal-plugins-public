from django.db import models
from django.utils import html
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OutputTimings(models.Model):
    item_id = models.CharField(max_length=255,unique=True,db_index=True)
    item_duration = models.FloatField(default=0.0)
    created_time = models.DateTimeField()
    version_created_time = models.DateTimeField()
    media_version = models.IntegerField()

    proxy_completed_interval = models.FloatField(blank=True,default=0.0)
    upload_trigger_interval = models.FloatField(blank=True,default=0.0)
    page_created_interval = models.FloatField(blank=True,default=0.0)
    capi_page_created_interval = models.FloatField(blank=True,default=0.0)

    final_transcode_completed_interval = models.FloatField(blank=True,default=0.0)

    page_launch_guess_interval = models.FloatField(blank=True,default=0.0)
    page_launch_capi_interval = models.FloatField(blank=True,default=0.0)
    page_launch_pluto_lag = models.FloatField(blank=True,default=0.0)
    completed_time = models.DateTimeField(blank=True)

    project = models.CharField(max_length=255,db_index=True,blank=True)
    commission = models.CharField(max_length=255,db_index=True,blank=True)

    class Meta:
        ordering = ['-completed_time','-created_time']

    @property
    def total_time_taken(self):
        return self.completed_time - self.created_time

    @property
    def proxy_completed_interval_ratio(self):
        return float(self.proxy_completed_interval)/float(self.item_duration)

    @property
    def proxy_completed_interval_diff(self):
        return float(self.proxy_completed_interval) #this is the first one, so there's nothing to subtract

    @property
    def upload_trigger_interval_ratio(self):
        return float(self.upload_trigger_interval_diff) / float(self.item_duration)

    @property
    def upload_trigger_interval_diff(self):
        return float(self.upload_trigger_interval) - float(self.proxy_completed_interval)

    @property
    def page_created_interval_ratio(self):
        return float(self.page_created_interval_diff) / float(self.item_duration)

    @property
    def page_created_interval_diff(self):
        return float(self.page_created_interval) - float(self.upload_trigger_interval)

    @property
    def final_transcode_completed_interval_ratio(self):
        return float(self.final_transcode_completed_interval_diff) / float(self.item_duration)

    @property
    def final_transcode_completed_interval_diff(self):
        return float(self.final_transcode_completed_interval) - float(self.page_created_interval)

    @property
    def page_launch_guess_interval_ratio(self):
        return float(self.page_launch_guess_interval) / float(self.item_duration)

    @property
    def page_launch_capi_interval_ratio(self):
        return float(self.page_launch_capi_interval_diff) / float(self.item_duration)

    @property
    def page_launch_capi_interval_diff(self):
        return float(self.page_launch_capi_interval) - float(self.final_transcode_completed_interval)

    @property
    def total_time_in_automation(self):
        totl = self.proxy_completed_interval_diff
        if self.page_created_interval_diff>0:
            totl += self.page_created_interval_diff
        if self.final_transcode_completed_interval_diff>0:
            totl += self.final_transcode_completed_interval_diff
        return totl

    @property
    def total_time_in_automation_ratio(self):
        return float(self.total_time_in_automation) / float(self.item_duration)

    @property
    def total_time_in_manual(self):
        return self.upload_trigger_interval_diff + self. page_launch_capi_interval_diff

    @property
    def total_time_in_manual_ratio(self):
        return float(self.total_time_in_manual) / float(self.item_duration)
