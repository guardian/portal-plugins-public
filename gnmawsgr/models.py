from django.db.models import Model,IntegerField,CharField,DateTimeField,BooleanField


class RestoreRequest(Model):
    requested_at = DateTimeField()
    completed_at = DateTimeField(blank=True,null=True)
    attempts = IntegerField()
    item_id = CharField(max_length=32)
    parent_collection = CharField(max_length=32,blank=True,null=True)
    username = CharField(max_length=512,default='admin')
    file_size = IntegerField(blank=True,null=True)
    currently_downloaded = IntegerField(blank=True,null=True)
    project_id = CharField(max_length=32,default='(unknown)')
    filepath_original = CharField(max_length=32768,blank=True)
    filepath_destination = CharField(max_length=32768,null=True)
    failure_reason = CharField(max_length=32768,blank=True,null=True)
    status = CharField(max_length=64,choices=(
        ('READY','Ready'),
        ('AWAITING_RESTORE','Awaiting Restore'),
        ('DOWNLOADING','Downloading'),
        ('IMPORTING','Importing'),
        ('COMPLETED','Completed'),
        ('RETRY','Retry'),
        ('FAILED','Failed'),
        ('NOT_GLACIER','Not Glacier')
    ))

    def __unicode__(self):
        return u'{u} restoring {i} at {t}, status {s}'.format(u=self.username,i=self.item_id,t=self.requested_at,
                                                              s=self.status)