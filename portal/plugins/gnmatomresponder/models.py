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
    atom_title = models.CharField(max_length=1024, default="Unknown title")
    user_email = models.CharField(max_length=1024, default="Unknow user", db_index=True)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True)
    s3_path = models.CharField(max_length=2048, null=True)

    class Meta:
        ordering = ['-started_at']

    def __unicode__(self):
        return u"Import of {0} from {1} to item {2}".format(self.atom_title, self.user_email, self.item_id)

    def __str__(self):
        return self.__unicode__().encode("ASCII","backslashreplace")