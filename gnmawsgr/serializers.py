from rest_framework.serializers import ModelSerializer


class BulkRestoreSerializer(ModelSerializer):
    class Meta:
        from models import BulkRestore
        model = BulkRestore
        fields = ('id','parent_collection', 'username', 'number_requested', 'number_queued', 'number_already_going', 'current_status', 'last_error')