from django.db.models import *


class KinesisTracker(Model):
    ST_NONE=0
    ST_SEEN=1
    ST_PROCESSING=2
    ST_DONE=3
    ST_ERROR=4

    stream_name = CharField(max_length=255,db_index=True)
    shard_id = CharField(max_length=255)
    sequence_number = CharField(max_length=255)
    status = IntegerField(default=ST_NONE)
    processing_host = CharField(max_length=255, null=True)
    millis_behind_latest = BigIntegerField()
    last_exception = CharField(max_length=2048, null=True)
    exception_trace = CharField(max_length=32768, null=True)
    created = DateTimeField()
    updated = DateTimeField()