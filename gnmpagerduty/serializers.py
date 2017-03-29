__author__ = 'dave'
from rest_framework.serializers import ModelSerializer
from models import StorageData


class StorageDataSerializer(ModelSerializer):
    class Meta:
        model = StorageData
        fields = ('storage_id','trigger_size')
