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

        rtn = {'status': 'ok', 'data': {'events': []}, 'aggregations': {},
               'start_time': start_time, 'end_time': end_time, 'include_aggregations': get_aggregations}

        i = ReutersIndex() #use settings value for cluster name
        for r in i.results_for_daterange(start_time,end_time,include_aggregations=get_aggregations,page=page,
                                         page_length=page_length,one_page=True):
            pprint(r)
            if isinstance(r,int):
                rtn['total'] = r
            elif isinstance(r,ReutersAggregation):
                rtn['aggregations'][r.name] = r.for_wordcloud()
            elif isinstance(r,ReutersEntry):
                rtn['data']['events'].append(r.for_timelinejs())
            else:
                rtn['data']['events'].append(r)

        return Response(rtn,status=200)


class GetVSClipView(APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer
    from rest_framework import permissions

    permission_classes = (permissions.IsAuthenticated, )
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    def get(self, request, category=None, es_id=None):
        from reutersindex import ReutersIndex
        from gnmvidispine.vs_search import VSItemSearch, VSSearchRange
        from gnmvidispine.vs_timecode import VSTimecode
        from django.conf import settings
        from dateutil.parser import parse

        i = ReutersIndex()
        data = i.specific_id(es_id)
        if data is None:
            return Response({'status': 'error','error': '{0} not found'.format(es_id)},status=404)

        s = VSItemSearch(url="http://dc1-mmmw-05.dc1.gnm.int",#url=settings.VIDISPINE_URL,
                         user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD,
                         run_as=self.request.user.pk)

        start_time = parse(data['_source']['start'])
        end_time = parse(data['_source']['end'])

        day_start = start_time.replace(hour=0,minute=0,second=0,microsecond=0)
        day_end = end_time.replace(hour=23,minute=59,second=59,microsecond=999)

        #s.debug=1
        #THOUGHT - this is getting messy. it would be better to put proper 'start' and 'end' fields on the VS records,
        #and then to search for them directly.
        s.addCriterion({'startTimeCode': VSSearchRange(start=VSTimecode(start_time,25), end=VSTimecode(end_time,25)),
                        'gnm_asset_category': category,
                        'created': VSSearchRange(start=day_start,end=day_end)})
        s.addSort('created','descending')

        print s._makeXML()
        result = s.execute()

        rtn = []

        print "Got a total of {0} results".format(result.totalItems)
        for r in result.results(shouldPopulate=False):
            print "Got {0}".format(r.name)
            rtn.append(r.name)

        return Response({'status': 'ok', 'results': rtn})