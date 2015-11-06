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
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from vsmixin import VSMixin

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


class InvalidPlutoType(StandardError):
    pass


class GetStatsView(VSMixin, APIView):
    recognised_types = {
        'commission': {
            'status_field': 'gnm_commission_status',
            'vs_class': 'collection'
        },
        'project': {
            'status_field': 'gnm_project_status',
            'vs_class': 'collection'
        },
        'master': {
            'status_field': 'gnm_master_generic_status',
            'vs_class': 'item'
        },
    }
    interesting_fields = []

    #temporary for debug
    vidispine_url = "http://pluto-dev.gnm.int"

    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer

    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(GetStatsView, self).dispatch(request, *args, **kwargs)

    def get(self, request, type=""):
        from traceback import format_exc
        try:
            return self.inner_get(request, type=type)
        except StandardError as e:
            return Response({'status': 'error', 'exception': str(e), 'trace': format_exc()},status=400)

    def inner_get(self, request, type=""):
        from xml.etree.cElementTree import Element,SubElement,tostring
        import httplib2
        import json
        from pprint import pprint

        if not type.lower() in self.recognised_types:
            raise InvalidPlutoType("{0} is not a recognised pluto type".format(type))

        xmlroot = Element('ItemSearchDocument', {'xmlns': 'http://xml.vidispine.com/schema/vidispine'})
        fieldEl = SubElement(xmlroot, 'field')
        nameEl = SubElement(fieldEl,'name')
        nameEl.text = 'gnm_type'
        valueEl = SubElement(fieldEl, 'value')
        valueEl.text=type
        facetEl = SubElement(xmlroot, 'facet', {'count': 'true'})
        ffieldEl = SubElement(facetEl, 'field')
        ffieldEl.text = self.recognised_types[type]['status_field']

        searchDoc = tostring(xmlroot,encoding="UTF-8")
        print searchDoc

        (headers, content) = self._make_vidispine_request(httplib2.Http(),"PUT","/API/search;number=0",searchDoc,
                                               {'Accept': 'application/json'})
        print "\nreturned:"
        print content

        data = json.loads(content)
        pprint(data)

        return Response({'status': 'ok', 'data': self.process_facets(data)})

    def process_facets(self,data):
        if not 'facet' in data:
            raise KeyError("Passed data does not contain facets")

        rtn = {}
        for block in data['facet']:
            rtn[block['field']] = (map(lambda x: {'category': x['fieldValue'], 'value': x['value']}, block['count']))
        return rtn
