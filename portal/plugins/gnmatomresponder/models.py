from django.db import models


class ImportJob(models.Model):
    item_id = models.CharField(max_length=64, db_index=True)
    job_id = models.CharField(max_length=64, db_index=True, unique=True)
    status = models.CharField(max_length=64, choices=[
        ('READY', 'Ready'),
        ('STARTED','Started'),
        ('FINISHED','Success'),
        ('FINISHED_WARNING','Non-fatal error'),
        ('FAILED_TOTAL','Failed'),
        ('WAITING', 'Waiting'),
        ('ABORT_PENDING', 'Abort requested'),
        ('ABORTED', 'Cancelled by admin')
    ])
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True)