"""
This is where you can write a lot of the code that responds to URLS - such as a page request from a browser
or a HTTP request from another application.

From here you can follow the Cantemo Portal Developers documentation for specific code, or for generic 
framework code refer to the Django developers documentation. 

"""
import logging

from django.contrib.auth.decorators import login_required
from portal.generic.baseviews import ClassView
from portal.vidispine.iitem import ItemHelper
from portal.vidispine.iexception import NotFoundError
from rest_framework.views import APIView
from rest_framework.response import Response

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


class ByDateRangeView(APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer
    from rest_framework import permissions

    permission_classes = (permissions.IsAuthenticated, )
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    def get(self, request):
        from datetime import datetime
        from dateutil.parser import parse
        from reutersindex import ReutersAggregation,ReutersIndex,ReutersEntry
        from pprint import pprint

        end_time = datetime.now()
        if 'end' in request.GET:
            try:
                end_time = parse(request.GET['end'])
            except ValueError as e:
                return Response({'status': 'error', 'error': unicode(e)},status=400)

        start_time = datetime.now().replace(hour=0,minute=0,second=0)
        if 'start' in request.GET:
            try:
                start_time = parse(request.GET['start'])
            except ValueError as e:
                return Response({'status': 'error', 'error': unicode(e)},status=400)

        page=0
        if 'p' in request.GET:
            page=int(request.GET['p'])

        page_length=100
        if 'l' in request.GET:
            page_length=int(request.get['l'])

        get_aggregations = False
        if 'agg' in request.GET:
            get_aggregations = True
            page_length=0

        rtn = {'status': 'ok', 'data': [], 'aggregations': {}, 'start_time': start_time, 'end_time': end_time, 'include_aggregations': get_aggregations}

        i = ReutersIndex() #use settings value for cluster name
        for r in i.results_for_daterange(start_time,end_time,include_aggregations=get_aggregations,page=page,
                                         page_length=page_length,one_page=True):
            pprint(r)
            if isinstance(r,int):
                rtn['total'] = r
            elif isinstance(r,ReutersAggregation):
                rtn['aggregations'][r.name] = r.for_wordcloud()
            elif isinstance(r,ReutersEntry):
                rtn['data'].append(r.for_timelinejs())
            else:
                rtn['data'].append(r)

        return Response(rtn,status=200)