from rest_framework.serializers import Serializer, ModelSerializer, CharField,DateTimeField


class ProjectSizeInfoSerializer(ModelSerializer):
    class Meta:
        from models import ProjectSizeInfoModel
        model = ProjectSizeInfoModel
        fields = ('project_id', 'storage_id', 'size_used_gb', 'last_updated', )


class ProjectScanReceiptSerializer(ModelSerializer):
    class Meta:
        from models import ProjectScanReceipt
        model = ProjectScanReceipt
        fields = ('project_id','last_scan','project_status', 'project_title', 'last_scan_duration', 'last_scan_error', )


class ProjectHistoryChangeSerializer(Serializer):
    fieldname = CharField(max_length=512)
    uuid = CharField(max_length=64)
    timestamp = DateTimeField()
    user = CharField(max_length=512)
    newvalue = CharField(max_length=512)