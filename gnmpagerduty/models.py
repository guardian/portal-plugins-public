from django.db.models import Model,BigIntegerField,IntegerField,CharField,DateTimeField


class StorageData(Model):
    storage_id = CharField(max_length=64,unique=True)
    trigger_size = BigIntegerField(blank=True,null=True)


class IncidentKeys(Model):
    storage_id = CharField(max_length=64,unique=True)
    incident_key = CharField(max_length=64,blank=True, default='')
