from django.db.models import Model,IntegerField,CharField,DateTimeField,BooleanField


class RestoreRequest(Model):
    requested_at = DateTimeField()
    completed_at = DateTimeField(blank=True,null=True)
    attempts = IntegerField()
    item_id = CharField(max_length=32)
    username = CharField(max_length=512,default='admin')
    file_size = IntegerField(blank=True,null=True)
    currently_downloaded = IntegerField(blank=True,null=True)
    project_id = CharField(max_length=32,default='(unknown)')
    filepath_original = CharField(max_length=32768,blank=True)
    filepath_destination = CharField(max_length=32768,null=True)
    status = CharField(max_length=64,choices=(
        ('READY','Ready'),
        ('AWAITING_RESTORE','Awaiting Restore'),
        ('DOWNLOADING','Downloading'),
        ('IMPORTING','Importing'),
        ('COMPLETED','Completed'),
        ('FAILED','Failed'),
        ('NOT_GLACIER','Not Glacier')
    ))
