__author__ = 'dave'
from rest_framework.serializers import ModelSerializer
from models import StorageData


class StorageDataSerializer(ModelSerializer):
    class Meta:
        model = StorageData
        fields = ('storage_id','maximum_size','current_size','trigger_size','incident_key')
