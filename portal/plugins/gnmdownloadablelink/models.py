from django.db.models import Model, CharField, ForeignKey, IntegerField, BooleanField, DateTimeField
from django.contrib.auth.models import User


class DownloadableLink(Model):
    class Meta:
        unique_together = (('item_id','shapetag'))

    public_url = CharField(max_length=512, blank=True)
    s3_url = CharField(max_length=512, blank=True)
    status = CharField(max_length=32, choices=[
        ("Requested", "Requested"),
        ("Transcoding", "Transcoding"),
        ("Upload Queued", "Upload Queued"),
        ("Uploading", "Uploading"),
        ("Available", "Available"),
        ("Failed", "Failed"),
        ("Retrying", "Retrying")
    ], db_index=True, default='Requested')
    created = DateTimeField()
    created_by = ForeignKey(to=User)
    expiry = DateTimeField()

    item_id = CharField(max_length=32,db_index=True)
    shapetag = CharField(max_length=64,db_index=True)
    transcode_job = CharField(max_length=32,blank=True,null=True)

    def __str__(self):
        return "{0} of {1} {2} expiring {3} at {4}".format(self.shapetag, self.item_id, self.status, self.expiry, self.s3_url)

    def save(self, *args, **kwargs):
        from django.utils import timezone
        if not self.id:
            self.created = timezone.now()
        return super(DownloadableLink, self).save(*args,**kwargs)