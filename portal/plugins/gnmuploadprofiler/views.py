"""
This is where you can write a lot of the code that responds to URLS - such as a page request from a browser
or a HTTP request from another application.

From here you can follow the Cantemo Portal Developers documentation for specific code, or for generic 
framework code refer to the Django developers documentation. 

"""
import logging

from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView
from django.http import HttpResponseBadRequest
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from portal.generic.baseviews import ClassView
from portal.vidispine.iitem import ItemHelper
from portal.vidispine.iexception import NotFoundError
from rest_framework.views import APIView
from rest_framework.response import Response
from models import OutputTimings
import re
from datetime import datetime

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


class DataMixin(object):
    """
    Mixin to abstract the shared data parts of display views
    """
    max_items = 100

    interesting_fields = [
        'item_duration',
        'proxy_completed_interval',
        'upload_trigger_interval',
        'page_created_interval',
        'final_transcode_completed_interval',
        'page_launch_guess_interval',
        'page_launch_capi_interval'
    ]

    def get_queryset(self):
        qs = OutputTimings.objects.all()

        if 'date' in self.request.GET:
            parts = re.match(r'(\d{4})(\d{2})(\d{2})', self.request.GET['date'])
            starting_time = datetime(year=int(parts.group(1)),
                                     month=int(parts.group(2)),
                                     day=int(parts.group(3)), )
            ending_time = datetime(year=int(parts.group(1)),
                                   month=int(parts.group(2)),
                                   day=int(parts.group(3)),
                                   hour=23, minute=59, second=59, microsecond=999999)

            qs = qs.filter(completed_time__gte=starting_time, completed_time__lt=ending_time)
        if 'commission' in self.request.GET:
            qs = qs.filter(commission=self.request.GET['commission'])
        if 'project' in self.request.GET:
            qs = qs.filter(project=self.request.GET['project'])
        if 'sort' in self.request.GET:
            qs = qs.order_by(self.request.GET['sort'])

        return qs

    @staticmethod
    def median_value(queryset, term):
        count = queryset.count()
        values = queryset.values_list(term, flat=True).order_by(term)
        if count % 2 == 1:
            return values[int(round(count / 2))]
        else:
            return sum(values[count / 2:count / 2 + 2]) / 2.0

    def calculate_averages(self,qs):
        from django.db.models import Avg, StdDev, Variance, Sum, Min, Max
        averages = {}

        for x in self.interesting_fields:
            # for x in OutputTimings._meta.get_all_field_names():
            data = qs.aggregate(Avg(x), StdDev(x), Min(x), Max(x))

            stkeyname = "{0}__stddev".format(x)
            avkeyname = "{0}__avg".format(x)

            if data[stkeyname] is None or data[avkeyname] is None:
                continue

            try:
                data[stkeyname] = "{0:.1f}%".format((data[stkeyname] / data[avkeyname]) * 100)
                averages.update(data)
            except ValueError: #if there is no data present then the division fails
                pass
        return averages


class AveragesRESTView(DataMixin, APIView):
    authentication_classes = (SessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer,)

    def get(self,request):
        from templatetags.uploadprofiler_customfilters import time_display
        qs = self.get_queryset()
        data = self.calculate_averages(qs)

        #if 'median' in self.request.GET:

        for fieldname in self.interesting_fields:
            data[fieldname + "__median"] = self.median_value(qs,fieldname)

        for k,v in data.items():
            if isinstance(v,float) or isinstance(v,int):
                keyname = k #+ "_formatted"
                data[keyname] = time_display(v)

        return Response(data)


class BasicDataView(DataMixin, ListView):
    model = OutputTimings
    template_name = "portal.plugins.gnmuploadprofiler/simple_data.html"

    def get_queryset(self):
        qs = super(BasicDataView, self).get_queryset()

        if 'date' in self.request.GET:
            parts = re.match(r'(\d{4})(\d{2})(\d{2})', self.request.GET['date'])
            starting_time = datetime(year=int(parts.group(1)),
                                     month=int(parts.group(2)),
                                     day=int(parts.group(3)), )
            ending_time = datetime(year=int(parts.group(1)),
                                   month=int(parts.group(2)),
                                   day=int(parts.group(3)),
                                   hour=23, minute=59, second=59, microsecond=999999)

            qs = qs.filter(completed_time__gte=starting_time, completed_time__lt=ending_time)
        if 'sort' in self.request.GET:
            qs = qs.order_by(self.request.GET['sort'])

        return qs

    def get_context_data(self, **kwargs):
        qs = kwargs['object_list']
        ctx = super(BasicDataView, self).get_context_data(**kwargs)
        #ctx['averages'] = qs.aggregate(Avg('item_duration'),StdDev('item_duration')))
        ctx['averages'] = self.calculate_averages(qs[:self.max_items])
        ctx['show_details'] = True
        if 'no_details' in self.request.GET:
            ctx['show_details'] = False
        ctx['show_totals'] = False
        if 'totals' in self.request.GET:
            ctx['show_totals'] = True
        return ctx


class ChartDataView(DataMixin, APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer,XMLRenderer
    from rest_framework import permissions

    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,XMLRenderer)

    def get_queryset(self):
        qs = super(ChartDataView,self).get_queryset()
        if "o" in self.request.GET:
            return qs.order_by(self.request.GET["o"])
        else:
            return qs

    def get(self,request):
        from serializers import OutputTimingsRatioSerializer
        qs = self.get_queryset()

        s = OutputTimingsRatioSerializer(qs[:25], many=True)
        return Response(s.data)


class ItemInfoAPIView(APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer
    from rest_framework import permissions

    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)

    interesting_fields = [
        'title',
        'gnm_commission_title',
        'gnm_project_headline',
        'gnm_commission_workinggroup'
    ]

    def get(self,request,itemid=None):
        import re
        from gnmvidispine.vs_item import VSItem
        from django.core import cache
        from django.conf import settings

        #not necessary, as this is already done by the url parser
        # if not re.match(r'\w{2}-\d+$',itemid):
        #     return HttpResponseBadRequest("Item ID invalid")

        c = cache.get_cache('default')

        rtn = c.get('portal.plugins.gnmuploadprofiler:item:{0}'.format(itemid))
        if rtn is None:
            item = VSItem(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,user=settings.VIDISPINE_USERNAME,
                          passwd=settings.VIDISPINE_PASSWORD)
            item.populate(itemid,specificFields=self.interesting_fields)

            rtn = {}
            for f in self.interesting_fields:
                rtn[f] = item.get(f)
            c.set('portal.plugins.gnmuploadprofiler:item:{0}'.format(itemid),rtn)
        return Response(rtn)