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
from django.views.generic import View
from portal.plugins.gnm_projects.views import ProjectNewView
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


class ProjectTemplateFileView(View):
    exclude_extensions = ['.lst','.pl','.py','.txt']

    def get(self,request,project_type=None):
        from django.conf import settings
        from django.http import HttpResponse, Http404
        import os.path
        import re

        if not hasattr(settings, 'PROJECT_FILE_CREATION_SCRIPT_TEMPLATE_ROOT'):
            raise ValueError("PROJECT_FILE_CREATION_SCRIPT_TEMPLATE_ROOT is not configured in settings")

        #sanitise the project_type value. / is allowed, but dangerous chars like .. are not.
        project_type = re.sub(r'[^A-Za-z/0-9_]','',project_type)

        filepath = os.path.join(settings.PROJECT_FILE_CREATION_SCRIPT_TEMPLATE_ROOT, project_type)
        log.debug("File path is {0}".format(filepath))

        desired_extensions = None

        if 'xtn' in request.GET:
            desired_extensions = request.GET['xtn'].split(',')

        file_list = []

        try:
            for f in os.listdir(filepath):
                if not os.path.isfile(os.path.join(filepath,f)): continue
                exclude = False
                for excluded in self.exclude_extensions:
                    if f.endswith(excluded):
                        exclude = True
                        break
                if exclude:
                    continue

                if desired_extensions is not None:
                    for desired in desired_extensions:
                        if not f.endswith(desired):
                            exclude = True
                            break
                if exclude:
                    continue

                file_list.append(f)
        except OSError as e:
            log.error(e)
            raise Http404

        if len(file_list) == 0:
            log.error("No files present in template directory {0} while excluding {1} and desiring {2}".format(
                filepath, self.exclude_extensions, desired_extensions
            ))
            raise Http404

        full_path = os.path.join(filepath,file_list[0])
        log.info("Sending file {0}".format(full_path))
        with open(full_path) as fp:
            return HttpResponse(fp.read(),content_type='application/octet-stream',status=200)


#this view requires login as it derives from another that does
class ProjectDefaultInformationView(ProjectNewView):
    def get(self, request):
        import json
        from django.http import HttpResponse
        from portal.plugins.gnm_commissions.models import VSCommission
        from portal.plugins.gnm_vidispine_errors.exceptions import VSHttp404

        parent_commission = self.kwargs.get('parent_commission')
        try:
            commission = VSCommission(parent_commission, self.request.user)
        except VSHttp404:
            return HttpResponse(json.dumps({'not_found': parent_commission}),status=404)

        return HttpResponse(json.dumps(self._initial_data(commission,request.user)))


class CachedViewMixin(object):
    def __init__(self,*args,**kwargs):
        import memcache
        from django.conf import settings
        super(CachedViewMixin,self).__init__(*args,**kwargs)

        self.mc = memcache.Client([settings.CACHE_LOCATION])


class GenericGroupListView(CachedViewMixin, APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer

    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    group_name = ""
    data_desc = "pluto:none"
    expiry_time=21600 #default: 6 hours

    def get_data(self,**kwargs):
        from vidispine.vs_globalmetadata import VSGlobalMetadata
        from django.conf import settings
        md = VSGlobalMetadata(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                              user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)

        md.populate()
        grp = md.get_group(self.group_name)
        return grp.values()

    def get(self,request,**kwargs):
        data = None
        if self.data_desc is not None:
            data = self.mc.get(self.data_desc)
        if data is None:
            data = self.get_data(**kwargs)
            if self.data_desc is not None:
                self.mc.set(self.data_desc,data,time=self.expiry_time)
        return Response({'status': 'ok', 'group_count': len(data), 'group_list': data})


class WorkingGroupListView(GenericGroupListView):
    group_name = "WorkingGroup"
    data_desc = "pluto:working_group_list_cache"


class CommissionerListView(GenericGroupListView):
    group_name = "Commissioner"
    data_desc = "pluto:commissioner_list_cache"


class ProjectTypeListView(GenericGroupListView):
    group_name = "ProjectType"
    data_desc = "pluto:project_types_list"


class ProjectSubTypeListView(GenericGroupListView):
    group_name = "ProjectSubType"
    data_desc = "pluto:project_sub_types:"
    #data_desc = None

    def get_data(self,**kwargs):
        #kwargs are passed through from the request
        from vidispine.vs_globalmetadata import VSGlobalMetadata
        from django.conf import settings
        from pprint import pprint
        md = VSGlobalMetadata(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                              user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)

        md.populate()
        grp = md.get_group(self.group_name)
        #pprint(grp.__dict__)
        rtn = []
        for v in grp.values():
            if v['gnm_projectsubtype_projecttype'] == kwargs['project_type']:
                rtn.append(v)

        return rtn

    def get(self,request,**kwargs):
        self.data_desc = "pluto:project_sub_types:{0}".format(kwargs['project_type'])
        return super(ProjectSubTypeListView,self).get(request,**kwargs)

class GenericListView(APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer

    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    interesting_fields = [
        'title',
        'gnm_project_type',
        'gnm_project_headline',
        'gnm_project_status',
        'gnm_type'
    ]

    def get(self, request, search_criteria={}, response_extra={},*args,**kwargs):
        from vidispine.vs_search import VSSearch
        from django.conf import settings
        from django.http import HttpResponseBadRequest
        import traceback
        import re

        try:
            s = VSSearch(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,port=settings.VIDISPINE_PORT,
                                   passwd=settings.VIDISPINE_PASSWORD, searchType="collection")
            s.debug = False
            s.addCriterion(search_criteria)

            result = s.execute()
            # if result.total_hits == 0:
            #     return Response({'status': 'ok', 'projects': 0})

            project_list = []
            for item in result.results(shouldPopulate=False):
                item.populate(item.name,specificFields=self.interesting_fields)
                rec = {'itemId': item.name}
                for f in self.interesting_fields:
                    rec[f] = item.get(f)
                project_list.append(rec)

            rsp = {'status': 'ok', 'count': len(project_list), 'list': project_list}
            rsp.update(response_extra)
            return Response(rsp)
        except Exception as e:
            if settings.DEBUG:
                return Response({'status': 'error', 'exception': str(e), 'trace': traceback.format_exc()},status=500)
            else:
                return Response({'status': 'error'},status=500)


class ProjectListView(GenericListView):
    interesting_fields = [
        'title',
        'gnm_project_type',
        'gnm_project_headline',
        'gnm_project_byline',
        'gnm_project_standfirst',
        'gnm_project_tags',
        'gnm_project_status',
        'gnm_type',

    ]

    def get(self, request, **kwargs):
        import re
        from django.http import HttpResponseBadRequest

        if not 'commission_id' in kwargs:
            return HttpResponseBadRequest()
        commission_id = kwargs['commission_id']

        if not re.match(r'\w{2}-\d+',commission_id):
            return HttpResponseBadRequest()

        criteria = {'__parent_collection': commission_id}
        return super(ProjectListView,self).get(request, search_criteria=criteria,response_extra={'commission': commission_id},
                                                  **kwargs)


class CommissionListView(GenericListView):
    interesting_fields = [
        'title',
        'gnm_commission_headline',
        'gnm_commission_status',
        'gnm_commission_workinggroup',
        'gnm_type'
    ]

    def get(self, request, *args,**kwargs):
        from django.http import HttpResponseBadRequest
        from pprint import pprint

        if not 'working_group' in kwargs:
            return HttpResponseBadRequest()

        criteria = {'gnm_commission_workinggroup': kwargs['working_group'],
                    'gnm_type': 'Commission'}
        pprint(criteria)
        return super(CommissionListView,self).get(request,search_criteria=criteria,**kwargs)