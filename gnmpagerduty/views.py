import logging
from portal.generic.baseviews import ClassView
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from models import StorageData
from django.conf import settings
from serializers import StorageDataSerializer
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
import traceback
from gnmvidispine.vs_storage import VSStoragePathMap

log = logging.getLogger(__name__)

class GenericAppView(ClassView):
    """ Show the page. Add your python code here to show dynamic content or feed information in
        to external apps
    """
    def __call__(self):
        # __call__ responds to the incoming request. It will already have a information associated to it, such as self.template and self.request

        log.debug("%s Viewing page" % self.request.user)
        ctx = {}

        # return a response to the request
        return self.main(self.request, self.template, ctx)

# setup the object, and decorate so that only logged in users can see it
GenericAppView = GenericAppView._decorate(login_required)


class StorageDataList(ListAPIView):
    queryset = StorageData.objects.all()
    serializer_class = StorageDataSerializer
    renderer_classes = (JSONRenderer, )


class StorageDataAdd(CreateAPIView):
    serializer_class = StorageDataSerializer
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )


class StorageDataUpdate(UpdateAPIView):

    serializer_class = StorageDataSerializer
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    def put(self, *args, **kwargs):

        try:
            data = self.request.DATA

            record = StorageData.objects.get(storage_id=data['storage_id'])
            record.trigger_size = int(data['trigger_size'])
            if record.incident_key is None:
                record.incident_key = ""
            record.save()

        except Exception as e:
            return Response({'status': 'error','exception': str(e), 'trace': traceback.format_exc()}, status=500)

        return self.response


class ConfigAlertsView(ListView):

    model = StorageData
    template_name = "gnmpagerduty/admin_list.html"

    def get_context_data(self, modelready=model, **kwargs):

        ctx = super(ConfigAlertsView, self).get_context_data(**kwargs)
        self.map = VSStoragePathMap(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                                    user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD,
                                    run_as=self.request.user.username)

        ctx['map'] = map(lambda (k,v): v.__dict__, self.map.items())

        n = 0

        for val in ctx['map']:
            print(val['name'])
            try:
                record = StorageData.objects.get(storage_id=val['name'])
                ctx['map'][n]['triggerSize'] = int(record.trigger_size)
            except Exception as e:
                ctx['map'][n]['triggerSize'] = 0
                print 'try code went wrong'

            n = (n + 1)

        return ctx
