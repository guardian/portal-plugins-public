"""
This is where you can write a lot of the code that responds to URLS - such as a page request from a browser
or a HTTP request from another application.

From here you can follow the Cantemo Portal Developers documentation for specific code, or for generic 
framework code refer to the Django developers documentation. 

"""
import logging

from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView
from portal.generic.baseviews import ClassView
from portal.vidispine.iitem import ItemHelper
from portal.vidispine.iexception import NotFoundError
from rest_framework.views import APIView
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


class BasicDataView(ListView):
    model = OutputTimings
    template_name = "gnmuploadprofiler/simple_data.html"

    def get_queryset(self):
        qs = super(BasicDataView,self).get_queryset()

        if 'date' in self.request.GET:
            parts = re.match(r'(\d{4})(\d{2})(\d{2})',self.request.GET['date'])
            starting_time = datetime(year=int(parts.group(1)),
                                     month=int(parts.group(2)),
                                     day=int(parts.group(3)),)
            ending_time = datetime(year=int(parts.group(1)),
                                     month=int(parts.group(2)),
                                     day=int(parts.group(3)),
                                   hour=23,minute=59,second=59,microsecond=999999)

            qs = qs.filter(completed_time__gte=starting_time,completed_time__lt=ending_time)
        if 'sort' in self.request.GET:
            qs = qs.order_by(self.request.GET['sort'])

        return qs

    def get_context_data(self, **kwargs):
        from django.db.models import Avg, StdDev, Variance,Sum, Min, Max

        qs = kwargs['object_list']
        averages = {}

        for x in ['item_duration','proxy_completed_interval','upload_trigger_interval',
                  'page_created_interval','final_transcode_completed_interval','page_launch_guess_interval']:
            data = qs.aggregate(Avg(x),StdDev(x),Min(x),Max(x))

            stkeyname = "{0}__stddev".format(x)
            avkeyname = "{0}__avg".format(x)

            data[stkeyname] = "{0:.1f}%".format((data[stkeyname]/data[avkeyname])*100)

            averages.update(data)

        ctx = super(BasicDataView, self).get_context_data(**kwargs)
        #ctx['averages'] = qs.aggregate(Avg('item_duration'),StdDev('item_duration')))
        ctx['averages'] = averages
        return ctx