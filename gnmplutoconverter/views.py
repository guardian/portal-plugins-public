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
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django.http import HttpResponseBadRequest

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


class WorkingGroupListView(APIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, )
    renderer_classes = (JSONRenderer, )

    def get(self, request):
        from portal.plugins.gnm_vidispine_utils.vs_helpers import working_groups

        return Response(working_groups)


class GenericSearchView(APIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, )
    renderer_classes = (JSONRenderer, )

    def get(self,request,*args,**kwargs):
        try:
            #from pprint import pprint
            rtn = []

            results = self.do_search()

            #pprint(results[0].md.__dict__)

            for c in results:
                rtn.append({'vsid': str(c.id),'title': unicode(c.md.title)})
            #pprint(results[0].md.__dict__)

            return Response(rtn)

        except Exception as e:
            from traceback import format_exc
            print "{0}: {1}".format(e.__class__.__name__,e.message)
            print format_exc()

    def do_search(self):
        pass


class CommissionListView(GenericSearchView):
    def do_search(self):
        from portal.plugins.gnm_commissions.models import VSCommission

        if not 'wg' in self.request.GET:
            return HttpResponseBadRequest()

        critera_string="""
            <gnm_commission_workinggroup>{0}</gnm_commission_workinggroup>
        """.format(self.request.GET['wg'])

        #return VSCommission.objects.filter(gnm_commission_workinggroup=self.request.GET['wg'])
        return VSCommission.vs_search(criteria=VSCommission.search_criteria(criteria=critera_string))


class ProjectListView(GenericSearchView):
    def do_search(self):
        from portal.plugins.gnm_projects.models import VSProject

        if not 'comm' in self.request.GET:
            return HttpResponseBadRequest()

        critera_string = """
            <__collection>{0}</__collection>
        """.format(self.request.GET['comm'])

        # return VSCommission.objects.filter(gnm_commission_workinggroup=self.request.GET['wg'])
        return VSProject.vs_search(criteria=VSProject.search_criteria(criteria=critera_string))
