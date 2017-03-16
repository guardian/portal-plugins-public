import logging
from portal.generic.baseviews import ClassView
from django.contrib.auth.decorators import permission_required, login_required
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from models import StorageData
from django.conf import settings
from serializers import StorageDataSerializer
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from gnmvidispine.vs_storage import VSStoragePathMap
import pprint as pprint
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
    def __init__(self):
        print 'test'
        log.info('test')
    serializer_class = StorageDataSerializer
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )


class StorageDataUpdate(UpdateAPIView):

    serializer_class = StorageDataSerializer
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    def __init__(self):
        print 'test from StorageDataUpdate'
        log.info('test from StorageDataUpdate')

    def put(self, *args, **kwargs):
        #from pprint import pprint
        #import traceback
        #try:
        #    super(StorageDataUpdate,self).put(*args,**kwargs)
        #except Exception as e:
        #    return Response({'status': 'error','exception': str(e), 'trace': traceback.format_exc()}, status=500)

        try:
            print 'Running from try 1'
            data = self.request.DATA

            record = StorageData.objects.get(storage_id=data['storage_id'])
            record.trigger_size = data['trigger_size']
            record.save()

        except Exception as e:
            print e
            print 'try code went wrong'

        #except StorageData.DoesNotExist:
        #    record = StorageData()
        return self.response


class ConfigAlertsView(ListView):
    #@method_decorator(permission_required('change_storage_alerts', login_url='/authentication/login', raise_exception=True))
    #def dispatch(self, request, *args, **kwargs):
    #    return super(ConfigAlertsView,self).dispatch(request,*args,**kwargs)
    model = StorageData
    template_name = "gnmpagerduty/admin_list.html"

    def get_context_data(self, modelready=model, **kwargs):
        from pprint import pprint
        ctx = super(ConfigAlertsView, self).get_context_data(**kwargs)
        self.map = VSStoragePathMap(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                                    user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD,
                                    run_as=self.request.user.username)
        pprint(self.map)

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

        #pprint(ctx['map'])
        #pprint(ctx['map'][0]['name'])
        #pprint(modelready.objects.values_list())
        #dirty = modelready.objects.values_list('trigger_size', flat=True)
        #try:
        #    ctx['data'] = int(dirty[0])
        #except Exception as e:
        #    ctx['data'] = 0

        return ctx


class AlertsEditView(UpdateView):
    @method_decorator(permission_required('change_storage_alerts', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(AlertsEditView,self).dispatch(request,*args,**kwargs)
    model = StorageData
    template_name = "gnmpagerduty/edit.html"
    success_url = reverse_lazy('gnmpagerduty_admin')

class AlertsDeleteView(DeleteView):
    @method_decorator(permission_required('change_storage_alerts', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(AlertsDeleteView,self).dispatch(request,*args,**kwargs)
    model = StorageData
    template_name = "gnmpagerduty/delete.html"
    success_url = reverse_lazy('gnmpagerduty_admin')

class AlertsCreateView(CreateView):
    @method_decorator(permission_required('change_storage_alerts', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(AlertsCreateView,self).dispatch(request,*args,**kwargs)
    model = StorageData
    template_name = "gnmpagerduty/edit.html"
    success_url = reverse_lazy('gnmpagerduty_admin')