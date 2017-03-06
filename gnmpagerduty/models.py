from django.db.models import Model,BigIntegerField,IntegerField,CharField,DateTimeField


class StorageData(Model):
    storage_id = CharField(max_length=64,unique=True)
    maximum_size = BigIntegerField(blank=True,null=True)
    current_size = BigIntegerField(blank=True,null=True)
    trigger_size = BigIntegerField(blank=True,null=True)

