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
from django.core.urlresolvers import reverse_lazy, reverse
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
    parser_classes = (JSONParser, XMLParser, )
    serializer_class = DownloadableLinkSerializer
    model = DownloadableLink

    # def create(self, request, *args, **kwargs):
    #     """
    #     Override definition of create to add in our own content
    #     :param request:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     from rest_framework import status
    #     if 'content' in kwargs:
    #         serializer = self.get_serializer(data=kwargs['content'], files=request.FILES)
    #     else:
    #         serializer = self.get_serializer(data=request.DATA, files=request.FILES)
    #
    #     if serializer.is_valid():
    #         self.pre_save(serializer.object)
    #         self.object = serializer.save(force_insert=True)
    #         self.post_save(self.object, created=True)
    #         headers = self.get_success_headers(serializer.data)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED,
    #                         headers=headers)
    #
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        from tasks import create_link_for
        from django.db import IntegrityError
        import json
        print request.DATA

        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        newdata = serializer.to_native(request.DATA)

        newdata['created_by'] = request.user
        newdata['item_id'] = kwargs['item_id']
        newdata['shapetag'] = kwargs['shape_tag']
        newdata['transcode_job'] = ""
        newdata['public_url'] = ""
        newdata['s3_url'] = ""
        print newdata

        existing_model_list = DownloadableLink.objects.filter(item_id=kwargs['item_id'], shapetag=kwargs['shape_tag'])
        if existing_model_list.count()>0:
            logger.info("{0}: Link already exists for {1}".format(kwargs['item_id'],kwargs['shape_tag']))

            for model in existing_model_list:
                #if a downloadable link already exists, then just redirect to that
                return HttpResponseRedirect(reverse_lazy("downloadable_link_item", kwargs={'pk': model.pk}))

        self.pre_save(serializer.object)
        #self.object = serializer.save(force_insert=True)
        try:
            self.object = DownloadableLink(**newdata)
            self.object.save()
        except IntegrityError as e:
            return Response({'status': 'error', 'error': 'Invalid input data', 'detail': str(e)}, status=400)

        self.post_save(self.object, created=True)

        resp_headers = self.get_success_headers(newdata)
        response = create_link_for.delay(kwargs['item_id'],kwargs['shape_tag'])
        return Response({'status': 'ok', 'link': reverse("downloadable_link_item", kwargs={'pk': self.object.id}), 'task': response.id})

#FIXME: change this to be a standard rest_client create view with the extra functionality bolted on
class CreateLinkRequestOld(APIView):
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