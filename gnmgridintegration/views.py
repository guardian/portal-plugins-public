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
from rest_framework import viewsets
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


class VSCallbackView(APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer
    from rest_framework import permissions

    permission_classes = (permissions.AllowAny, )
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    def post(self, request):
        from notification_handler import get_new_thumbnail
        from pprint import pprint
        #try:
        pprint(request.DATA)
        get_new_thumbnail(request.DATA)
        return Response({'status': 'ok', 'information': 'Not implemented', 'sent': request.DATA}, status=200)
        # except TypeError as e:
        #     return Response({'status': 'error', 'exception': str(e)},status=400)
