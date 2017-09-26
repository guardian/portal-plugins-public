"""
This is where you can write a lot of the code that responds to URLS - such as a page request from a browser
or a HTTP request from another application.

From here you can follow the Cantemo Portal Developers documentation for specific code, or for generic 
framework code refer to the Django developers documentation. 

"""
import logging
from rest_framework.generics import ListAPIView
from rest_framework.renderers import JSONRenderer, XMLRenderer
from rest_framework.permissions import IsAdminUser
from serializers import KinesisTrackerSerializer
from django.contrib.auth.decorators import login_required

log = logging.getLogger(__name__)


class MessageListView(ListAPIView):
    serializer_class = KinesisTrackerSerializer
    permission_classes = (IsAdminUser, )
    renderer_classes = (JSONRenderer, XMLRenderer)

    def get_queryset(self):
        from models import KinesisTracker
        stream_name = self.kwargs['stream_name']
        return KinesisTracker.objects.filter(stream_name=stream_name)
