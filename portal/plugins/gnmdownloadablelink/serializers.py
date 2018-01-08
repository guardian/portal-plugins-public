from rest_framework.serializers import ModelSerializer
from models import DownloadableLink


class DownloadableLinkSerializer(ModelSerializer):
    def __init__(self,*args,**kwargs):
        super(DownloadableLinkSerializer,self).__init__(*args,**kwargs)
        if 'defaults' in kwargs:
            self.defaults = kwargs['defaults']

    class Meta:
        model = DownloadableLink
        fields = ('public_url', 'status', 'created', 'created_by',
                  'expiry', 'item_id', 'shapetag', 'transcode_job')
