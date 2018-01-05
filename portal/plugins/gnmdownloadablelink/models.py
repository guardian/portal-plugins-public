from django.db.models import Model, CharField, ForeignKey, IntegerField, BooleanField, DateTimeField
from django.contrib.auth.models import User


class DownloadableLink(Model):
    class Meta:
        unique_together = (('item_id','shapetag'))

    public_url = CharField(max_length=512, blank=True)
    status = CharField(max_length=32, choices=[
        ("Requested", "Requested"),
        ("Transcoding", "Transcoding"),
        ("Uploading", "Uploading"),
        ("Available", "Available"),
        ("Failed", "Failed")
    ])
    created = DateTimeField()
    created_by = ForeignKey(to=User)
    expiry = DateTimeField()

    item_id = CharField(max_length=32,db_index=True)
    shapetag = CharField(max_length=64,db_index=True)
    transcode_job = CharField(max_length=32,blank=True)