from rest_framework.serializers import ModelSerializer

from models import DownloadableLink


class DownloadableLinkSerializer(ModelSerializer):
    class Meta:
        model = DownloadableLink
        fields = ('public_url', 'status', 'created', 'created_by',
                  'expiry', 'item_id', 'shapetag', 'transcode_job')