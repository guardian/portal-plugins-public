from django.db.models import Model, IntegerField, CharField, DateTimeField
from datetime import datetime


class ProjectSizeInfoModel(Model):
    project_id = CharField(max_length=32, db_index=True)
    storage_id = CharField(max_length=32, db_index=True)
    size_used_gb = IntegerField()
    last_updated = DateTimeField(default=datetime.now)

    class Meta:
        unique_together = (("project_id", "storage_id",))
