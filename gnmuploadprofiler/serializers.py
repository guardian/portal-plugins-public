from rest_framework import serializers
from models import OutputTimings


class OutputTimingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutputTimings


class OutputTimingsRatioSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    item_duration = serializers.FloatField()
    proxy_completed_interval_ratio = serializers.FloatField()
    upload_trigger_interval_ratio = serializers.FloatField()
    page_created_interval_ratio = serializers.FloatField()
    final_transcode_completed_interval_ratio = serializers.FloatField()
    #page_launch_guess_interval_ratio = serializers.FloatField()
    page_launch_capi_interval_ratio = serializers.FloatField()

    def create(self, validated_data):
        print "called serializer::create"
        pass

    def update(self, instance, validated_data):
        print "called serializer::update"
        pass


class OutputTimingsDiffSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    item_duration = serializers.FloatField()
    proxy_completed_interval_diff = serializers.FloatField()
    upload_trigger_interval_diff = serializers.FloatField()
    page_created_interval_diff = serializers.FloatField()
    final_transcode_completed_interval_diff = serializers.FloatField()
    #page_launch_guess_interval_diff = serializers.FloatField()
    page_launch_capi_interval_diff = serializers.FloatField()