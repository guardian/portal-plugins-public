from rest_framework.serializers import ModelSerializer
from portal.plugins.kinesisresponder.models import KinesisTracker


class KinesisTrackerSerializer(ModelSerializer):
    class Meta:
        model = KinesisTracker