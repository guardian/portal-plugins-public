"""
This is where you can write a lot of the code that responds to URLS - such as a page request from a browser
or a HTTP request from another application.

From here you can follow the Cantemo Portal Developers documentation for specific code, or for generic 
framework code refer to the Django developers documentation. 

"""
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, XMLRenderer
from serializers import DownloadableLinkSerializer
from models import DownloadableLink
from django.core.urlresolvers import reverse_lazy
from datetime import datetime, timedelta
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class LinksForItem(ListAPIView):
    renderer_classes = (JSONRenderer, XMLRenderer, )
    permission_classes = (IsAuthenticated, )
    serializer_class = DownloadableLinkSerializer
    model = DownloadableLink

    def get_queryset(self):
        return DownloadableLink.objects.filter(item_id=self.request.GET['itemid'])


class GetLink(RetrieveAPIView):
    renderer_classes = (JSONRenderer, XMLRenderer, )
    permission_classes = (IsAuthenticated, )
    serializer_class = DownloadableLinkSerializer
    model = DownloadableLink


class CreateLinkRequest(APIView):
    renderer_classes = (JSONRenderer, XMLRenderer, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, item_id=None, shape_tag=None):
        from tasks import create_link_for
        import dateutil.parser
        logger.info("{0}: Creating link for {1}".format(item_id, shape_tag))

        existing_model_list = DownloadableLink.objects.filter(item_id=item_id, shapetag=shape_tag)
        if existing_model_list.count()>0:
            logger.info("{0}: Link already exists for {1}".format(item_id,shape_tag))

            for model in existing_model_list:
                #if a downloadable link already exists, then just redirect to that
                return HttpResponseRedirect(reverse_lazy("downloadable_link_item", kwargs={'pk': model.pk}))

        if 'expiry' in request.GET:
            expirytime = dateutil.parser.parse(request.GET['expiry'])
        else:
            expirytime = datetime.now() + timedelta(days=1)

        #ok, it does not exist.
        #create a record
        record = DownloadableLink(
            status="Requested",
            created=datetime.now(),
            created_by=request.user,
            item_id=item_id,
            expiry=expirytime,
            shapetag=shape_tag
        )
        record.save()
        #and kick off the job to create it
        create_link_for.delay(item_id,shape_tag)

        return Response({'status': 'not implemented'})