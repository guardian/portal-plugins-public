from django.db.models import Model,IntegerField,CharField,DateTimeField,BooleanField


class RestoreRequest(Model):
    requested_at = DateTimeField()
    completed_at = DateTimeField(blank=True,null=True)
    attempts = IntegerField()
    item_id = CharField(max_length=32)
    status = CharField(max_length=64,choices=(
        ('READY','Ready'),
        ('AWAITING_RESTORE','Awaiting Restore'),
        ('DOWNLOADING','Downloading'),
        ('IMPORTING','Importing'),
        ('COMPLETED','Completed'),
        ('FAILED','Failed'),
        ('NOT_GLACIER','Not Glacier')
    ))
