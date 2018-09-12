from django.db import models

#technically this does not belong here but it needs to be called late in every init, in order to register signals but import
#from other modules' .tasks
from .signals import *
setup_signals()


class ImportJob(models.Model):
    item_id = models.CharField(max_length=64, db_index=True)
    job_id = models.CharField(max_length=64, db_index=True, unique=True)
    atom_id = models.CharField(max_length=64,db_index=True)
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
    atom_title = models.CharField(max_length=1024, default="Unknown title")
    user_email = models.CharField(max_length=1024, default="Unknown user", db_index=True)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True)
    s3_path = models.CharField(max_length=2048, null=True)
    retry_number = models.IntegerField(default=0)
    processing = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']

    def is_failed(self):
        """
        Returns a boolean indicating whether the status of this job represents any kind of failure
        :return:
        """
        if self.status=='FAILED_TOTAL' or self.status=='FINISHED_WARNING' or self.status=='ABORTED':
            return True
        else:
            return False

    def previous_attempt(self):
        """
        Either returns the job reference of the previous attempt of this import, or None
        :return: an ImportJob instance or None
        """
        for entry in ImportJob.objects.filter(atom_id=self.atom_id).order_by('-retry_number')[:1]:
            return entry
        return None

    def __unicode__(self):
        return u"Import of {0} from {1} to item {2}".format(self.atom_title, self.user_email, self.item_id)

    def __str__(self):
        return self.__unicode__().encode("ASCII","backslashreplace")


class PacFormXml(models.Model):
    atom_id = models.CharField(max_length=64, db_index=True, unique=True)
    received = models.DateTimeField()
    completed = models.DateTimeField(blank=True, null=True)
    pacdata_url = models.CharField(max_length=4096)
    status = models.CharField(max_length=32, choices=[
        ("UNPROCESSED", "Unprocessed"),
        ("DOWNLOADING", "Downloading"),
        ("INPROGRESS", "In progress"),
        ("PROCESSED", "Processed"),
        ("ERROR", "Error")
    ], default="UNPROCESSED",db_index=True)
    celery_task_id = models.CharField(max_length=64, db_index=True, null=True)
    last_error = models.TextField(blank=True)
