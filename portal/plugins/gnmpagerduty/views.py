import logging
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.core.exceptions import ObjectDoesNotExist
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

raven_client = None
try:
    import raven
    raven_client = raven.Client(settings.RAVEN_CONFIG['dsn'])
except ImportError:
    log.error("Raven client not installed - can't log errors to Sentry")
except KeyError:
    log.error("Raven is installed but RAVEN_CONFIG is not set up properly. Can't log errors to Sentry.")
except AttributeError:
    log.error("Raven is installed but RAVEN_CONFIG is not set up properly. Can't log errors to Sentry.")


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
            record.save()

        except StandardError as e:
            log.error(traceback.format_exc())
            if raven_client is not None:
                raven_client.captureException()
            return Response({'status': 'error','exception': str(e), 'trace': traceback.format_exc()}, status=500)

        return Response({'status': "ok"})


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
            try:
                record = StorageData.objects.get(storage_id=val['name'])
                ctx['map'][n]['triggerSize'] = int(record.trigger_size)
            except ObjectDoesNotExist as e:
                log.error(traceback.format_exc())
                if raven_client is not None:
                    raven_client.captureException()
                ctx['map'][n]['triggerSize'] = 0
            except StandardError as e:
                log.error(traceback.format_exc())
                if raven_client is not None:
                    raven_client.captureException()
                ctx['map'][n]['triggerSize'] = 0

            n = (n + 1)

        return ctx
