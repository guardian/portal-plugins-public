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
from rest_framework.parsers import JSONParser, FormParser
from django.http import HttpResponseBadRequest
from django.conf import settings

logger = logging.getLogger(__name__)

raven_client = None
try:
    import raven
    raven_client = raven.Client(settings.RAVEN_CONFIG['dsn'])
except ImportError:
    logger.error("Raven client not installed - can't log errors to Sentry")
except KeyError:
    logger.error("Raven is installed but RAVEN_CONFIG is not set up properly. Can't log errors to Sentry.")
    
    
class GenericAppView(ClassView):
    """ Show the page. Add your python code here to show dynamic content or feed information in
        to external apps
    """
    def __call__(self):
        # __call__ responds to the incoming request. It will already have a information associated to it, such as self.template and self.request

        logger.debug("%s Viewing page" % self.request.user)
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
            from pprint import pprint
            rtn = []
            results = self.do_search()
            # print "Current user ID: {0}".format(request.user.pk)
            # pprint(results)
            for c in results:
                i={
                    'vsid': str(c.id),
                    'title': unicode(c.md.title),
                }

                #these might not exist so wrap in exception catching block
                try:
                    i['gnm_commission_status'] = unicode(c.md.gnm_commission_status)
                    i['user_id'] = unicode(c.md.gnm_commission_owner)
                except AttributeError:
                    pass

                try:
                    i['gnm_project_status'] = unicode(c.md.gnm_project_status)
                    i['user_id'] = unicode(c.md.gnm_project_owner)
                except AttributeError:
                    pass

                rtn.append(i)

            return Response(rtn)

        except StandardError as e:
            from traceback import format_exc
            logger.error(format_exc())
            if raven_client is not None:
                raven_client.captureException()
            return Response({'status': 'error', 'error': format_exc()}, status=500)

    def do_search(self):
        pass


class CommissionListView(GenericSearchView):
    def do_search(self):
        from portal.plugins.gnm_commissions.models import VSCommission

        if not 'wg' in self.request.GET:
            return HttpResponseBadRequest()

        critera_string="""
            <gnm_commission_workinggroup>{0}</gnm_commission_workinggroup>
            <OR>
                <gnm_commission_status>New</gnm_commission_status>
                <gnm_commission_status>In production</gnm_commission_status>
            </OR>
        """.format(self.request.GET['wg'])

        if 'mine' in self.request.GET:
            if self.request.GET['mine'] == 'true':
                critera_string += "<gnm_commission_owner>{0}</gnm_commission_owner>".format(self.request.user.pk)

        return VSCommission.vs_search(criteria=VSCommission.search_criteria(criteria=critera_string))


class ProjectListView(GenericSearchView):
    def do_search(self):
        from portal.plugins.gnm_projects.models import VSProject

        if not 'comm' in self.request.GET:
            return HttpResponseBadRequest()

        critera_string = """
            <__parent_collection>{0}</__parent_collection>
            <OR>
                <gnm_project_status>New</gnm_project_status>
                <gnm_project_status>In production</gnm_project_status>
            </OR>
        """.format(self.request.GET['comm'])

        if 'mine' in self.request.GET:
            if self.request.GET['mine'] == 'true':
                critera_string+="<gnm_project_owner>{0}</gnm_project_owner>".format(self.request.user.pk)

        # return VSCommission.objects.filter(gnm_commission_workinggroup=self.request.GET['wg'])
        return VSProject.vs_search(criteria=VSProject.search_criteria(criteria=critera_string))


class DoConversionView(APIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, )
    renderer_classes = (JSONRenderer, )
    parser_classes = (FormParser, JSONParser, )

    def post(self, request):
        from pprint import pformat
        from gnmvidispine.vidispine_api import VSException
        from gnmvidispine.vs_item import VSItem
        from gnmvidispine.vs_collection import VSCollection
        from gnmvidispine.vs_metadata import VSMetadata
        from django.conf import settings
        from portal.plugins.gnm_masters.models import VSMaster, MasterModel
        from portal.plugins.gnm_projects.models import VSProject
        from django.contrib.auth.models import User
        import re

        is_vsid = re.compile(r'^\w{2}-\d+')

        try:
            comm_id = request.POST['plutoconverter_commission_id_input']
            proj_id = request.POST['plutoconverter_project_id_input']
            item_id = request.POST['plutoconverter_item_id_input']
        except StandardError as e:
            return Response({'status': 'error', 'error': unicode(e)},status=400)

        if not is_vsid.match(comm_id) or not is_vsid.match(proj_id) or not is_vsid.match(item_id):
            return Response({'status': 'error', 'error': 'Not a valid Vidispine ID'},status=400)

        try:
            item = VSItem(user=settings.VIDISPINE_USERNAME, passwd=settings.VIDISPINE_PASSWORD, url=settings.VIDISPINE_URL)
            item.populate(item_id)

            if item.get('gnm_type') == 'master':
                return Response({'status': 'error', 'error': '{0} is already a master'.format(item_id)},status=400)

            project = VSCollection(user=settings.VIDISPINE_USERNAME, passwd=settings.VIDISPINE_PASSWORD, url=settings.VIDISPINE_URL)
            project.populate(proj_id)

            commission_id = project.get('__parent_collection')
            logger.info("Project {0} belongs to commission {1}".format(project.name, commission_id))

            commission = VSCollection(user=settings.VIDISPINE_USERNAME, passwd=settings.VIDISPINE_PASSWORD, url=settings.VIDISPINE_URL)
            commission.populate(commission_id)

            md_to_set = {
                'gnm_commission_title'         : commission.get('gnm_commission_title'),
                'gnm_commission_workinggroup'  : commission.get('gnm_commission_workinggroup'),
                'gnm_project_headline'         : project.get('gnm_project_headline'),
                'gnm_master_website_headline'  : item.get('title'),
                'gnm_master_website_standfirst': item.get('gnm_asset_description'),
                'gnm_master_website_byline'    : item.get('gnm_asset_owner'),
                # 'gnm_master_website_tags': breakout_tags(item.get('gnm_asset_user_keywords',allowArray=True),
                #                                         host=options.vshost,user=options.vsuser,passwd=options.vspasswd),
                'gnm_type'                     : 'Master',
                'gnm_master_language'          : settings.LANGUAGE_CODE[0:2],
            }

            logger.info("Going to add {0} to project {1}".format(item_id,md_to_set))
            project.addToCollection(item)
            logger.info("Going to set metadata on {0}: {1}".format(item_id, md_to_set))
            item.set_metadata(md_to_set)
            logger.info("SUCCESS: item {0} has been converted to master".format(item_id))

            admin_user = User.objects.get(username=settings.VIDISPINE_USERNAME)

            vs_project = VSProject(proj_id, admin_user)
            vs_master = VSMaster(item_id, admin_user)
            vs_project.add_master(vs_master)

            return Response({'status': 'success', 'itemid': item_id },status=200)
        except VSException as e:
            if raven_client is not None:
                raven_client.captureException()
            return Response({'status': 'error', 'error': "Vidispine said {0}".format(unicode(e))},status=500)
        except StandardError as e:
            if raven_client is not None:
                raven_client.captureException()
            return Response({'status': 'error', 'error': unicode(e)},status=500)

