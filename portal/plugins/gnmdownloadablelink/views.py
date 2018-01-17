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
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, XMLRenderer
from rest_framework.parsers import JSONParser, XMLParser
from serializers import DownloadableLinkSerializer
from models import DownloadableLink
from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse_lazy, reverse
import requests
import django.db
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


class CreateLinkRequest(CreateAPIView):
    renderer_classes = (JSONRenderer,XMLRenderer, )
    parser_classes = (JSONParser,  )
    serializer_class = DownloadableLinkSerializer
    model = DownloadableLink

    def post(self, request, *args, **kwargs):
        from tasks import create_link_for

        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        newdata = serializer.to_native(request.DATA)

        newdata['created_by'] = request.user.id
        newdata['status'] = 'Requested' if not 'status' in newdata or newdata['status'] is None else newdata['status']
        newdata['item_id'] = kwargs['item_id']
        newdata['shapetag'] = kwargs['shape_tag']
        newdata['transcode_job'] = ""
        newdata['public_url'] = ""
        newdata['s3_url'] = ""

        newserializer = self.get_serializer(data=newdata)
        if not newserializer.is_valid(): #construct a second serializer to validate the updated data
            return Response(newserializer.errors, status=400)

        logger.info("Checking existing links")
        existing_model_list = DownloadableLink.objects.filter(item_id=kwargs['item_id'], shapetag=kwargs['shape_tag'])
        if existing_model_list.count()>0:
            logger.info("{0}: Link already exists for {1}".format(kwargs['item_id'],kwargs['shape_tag']))

            for model in existing_model_list:
                #if a downloadable link already exists, then just redirect to that
                return HttpResponseRedirect(reverse_lazy("downloadable_link_item", kwargs={'pk': model.pk}))

        logger.info("No existing links found. Issuing pre-save signal")
        self.pre_save(serializer.object)

        logger.info("Saving new link record")
        self.object = newserializer.save(force_insert=True)


        logger.info("Done, issuing post-save signal")
        self.post_save(self.object, created=True)

        resp_headers = self.get_success_headers(newdata)
        logger.info("Triggering background task to transcode/upload")
        response = create_link_for.delay(kwargs['item_id'],kwargs['shape_tag'])
        logger.info("Returning")
        return Response({'status': 'ok', 'link': reverse("downloadable_link_item", kwargs={'pk': self.object.id}), 'task': response.id})


class RetryLinkRequest(APIView):
    renderer_classes = (JSONRenderer,XMLRenderer, )
    parser_classes = (JSONParser,  )
    serializer_class = DownloadableLinkSerializer
    model = DownloadableLink

    def post(self, request, *args, **kwargs):
        from tasks import create_link_for

        try:
            model = self.model.objects.get(pk=kwargs['pk'])
        except self.model.DoesNotExist:
            return Response({'status': 'error', 'error': 'invalid request'}, status=400)

        model.status="Retrying" #change the status from Failed, so that the UI knows to keep checking it
        model.save()
        logger.info("Retry link: triggering background task to transcode/upload")
        response = create_link_for.delay(model.item_id, model.shapetag)
        logger.info("Returning")
        return Response({'status': 'ok', 'link': reverse("downloadable_link_item", kwargs={'pk': model.id}), 'task': response.id})


class ShapeTagList(View):
    def get(self, request):
        from django.conf import settings
        url = "{0}:{1}/API/shape-tag?run-as={2}".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT, request.user.username)
        auth = (settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD,)

        response = requests.get(url, auth=auth, headers={'Accept': 'application/json'})
        return HttpResponse(response.content,content_type='application/json',status=response.status_code)