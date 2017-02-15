from django.db.models import Model,BigIntegerField,IntegerField,CharField,DateTimeField,BooleanField, ManyToOneRel
import re
from datetime import datetime

is_vidispine_id = re.compile(r'^\w{2}-\d+')


class RestoreRequest(Model):
    requested_at = DateTimeField()
    completed_at = DateTimeField(blank=True,null=True)
    attempts = IntegerField()
    item_id = CharField(max_length=32)
    parent_collection = CharField(max_length=32,blank=True,null=True)
    username = CharField(max_length=512,default='admin')
    file_size = BigIntegerField(blank=True,null=True)
    currently_downloaded = BigIntegerField(blank=True,null=True)
    project_id = CharField(max_length=32,default='(unknown)')
    filepath_original = CharField(max_length=32768,blank=True)
    filepath_destination = CharField(max_length=32768,null=True)
    failure_reason = CharField(max_length=32768,blank=True,null=True)
    file_size_check = CharField(max_length=32768,null=True)
    import_job = CharField(max_length=64,null=True,blank=True)
    status = CharField(max_length=64,choices=(
        ('READY','Ready'),
        ('AWAITING_RESTORE','Awaiting Restore'),
        ('DOWNLOADING','Downloading'),
        ('IMPORTING','Importing'),
        ('COMPLETED','Completed'),
        ('RETRY','Retry'),
        ('FAILED','Failed'),
        ('IMPORT_FAILED','Import Failed'),
        ('NOT_GLACIER','Not Glacier')
    ))

    def __unicode__(self):
        return u'{u} restoring {i} at {t}, status {s}'.format(u=self.username,i=self.item_id,t=self.requested_at,
                                                              s=self.status)

    class Meta:
        ordering = ['-requested_at','-completed_at','username','-item_id']
        

def restore_request_for(itemid, username=None, parent_project=None, rqstatus=None):
    """
    Will either return the current restore request for the given item ID, or it will create a new one
    :param itemid: item ID to get the request for
    :return: RestoreRequest (saved)
    """
    if not is_vidispine_id.match(itemid): raise ValueError("restore_request_for needs a valid Vidispine ID")
    
    try:
        rq = RestoreRequest.objects.get(item_id=itemid)
    except RestoreRequest.DoesNotExist:
        rq = RestoreRequest()
        rq.requested_at = datetime.now()
        rq.username = username
        rq.parent_collection = parent_project
        rq.status = rqstatus
        rq.attempts = 1
        rq.item_id = itemid
        rq.save()
    return rq
        
        
class BulkRestore(Model):
    parent_collection = CharField(max_length=32, unique=True)
    username = CharField(max_length=512, default='admin')
    
    number_requested = IntegerField()
    number_queued = IntegerField()
    number_already_going = IntegerField()
    
    current_status = CharField(max_length=32,choices=(
        ('Queued','Queued'),
        ('Processing', 'Processing'),
        ('Failed', 'Failed'),
        ('Completed', 'Completed')
    ), default="Queued")
    last_error = CharField(max_length=1024,null=True,blank=True)