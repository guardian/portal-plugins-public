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
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

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
    #FIXME: need to check authenticated
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

        file_index = 0
        if 'xtn' in request.GET:
            desired_extensions = request.GET['xtn'].split(',')
        if 'n' in request.GET:
            file_index = request.GET['n']

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

        if file_index>len(file_list):
            log.error("Client requested file index {0} but there are only {1} to choose from",file_index,len(file_list))
        full_path = os.path.join(filepath,file_list[file_index])
        log.info("Sending file {0}".format(full_path))
        with open(full_path) as fp:
            rsp = HttpResponse(fp.read(),content_type='application/octet-stream',status=200)
            rsp['X-Pluto-Filename'] = os.path.basename(fp.name)
            rsp['X-Pluto-Filecount'] = len(file_list)
            return rsp


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


class ProjectMakeView(APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer
    from rest_framework.permissions import IsAuthenticated

    permission_classes= (IsAuthenticated, )
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    def post(self,request, **kwargs):
        from portal.plugins.gnm_projects.models import VSProject
        from portal.plugins.gnm_commissions.models import VSCommission
        from portal.plugins.gnm_commissions.exceptions import NotACommissionError
        from portal.plugins.gnm_vidispine_utils.models import Reference
        from portal.plugins.gnm_vidispine_utils import constants as const
        from forms import CustomisedProjectForm
        from pprint import pprint
        from django.http import Http404
        from tasks import complete_project_setup
        import json
        from django.contrib import messages
        commission_id = kwargs['commission_id']
        try:
            commission = VSCommission(commission_id, self.request.user)
        except NotACommissionError:
            '''
            FIXME
            display that someone is trying to create a project that wont belong to a commission
            and that is verboten!
            Probably shouldn't raise a 404 but it's something
            '''
            raise Http404

        form = CustomisedProjectForm(request.DATA)
        if form.is_valid():
            data = form.cleaned_data
            references = []
            commission_workinggroup_uuid = commission.get_workinggroup_reference_uuid()
            commission_title_uuid = commission.get_title_reference_uuid()
            if commission_workinggroup_uuid is not None:
                references.append(Reference(name=const.GNM_COMMISSION_WORKINGGROUP, uuid=commission_workinggroup_uuid))
            if commission_title_uuid is not None:
                references.append(Reference(name=const.GNM_COMMISSION_TITLE, uuid=commission_title_uuid))
        else:
            pprint(request.DATA)
            pprint({'status': 'error','error': 'invalid data',
                             'detail': [(k, unicode(v[0])) for k,v in form.errors.items()]})
            return Response({'status': 'error','error': 'invalid data',
                             'detail': [(k, unicode(v[0])) for k,v in form.errors.items()]},
                            status=400)

        # Create collection with metadata
        project = VSProject.vs_create(data, request.user, references=references)
        #request_data = json.dumps(request.__dict__)
        complete_project_setup.delay(commission_id,unicode(project.md.collectionId),user_id=request.user)

        # print project.md.__class__
        # pprint(project.md.__dict__)
        # meta = {}
        # for k,v in project.md.__dict__.items(): #this is a dictproxy so i can't get at it directly
        #     meta[k] = v
        # pprint(meta)
        messages.info(request, 'Project created')

        return Response({'status': 'ok', 'project_id': unicode(project.md.collectionId), 'commission_id': commission_id},status=200)


class CachedViewMixin(object):
    def __init__(self,*args,**kwargs):
        import memcache
        from django.conf import settings
        super(CachedViewMixin,self).__init__(*args,**kwargs)

        self.mc = memcache.Client([settings.CACHE_LOCATION])


class GenericGroupListView(CachedViewMixin, APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer
    from rest_framework.permissions import IsAuthenticated

    permission_classes= (IsAuthenticated, )
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    group_name = ""
    data_desc = "pluto:none"
    expiry_time=21600 #default: 6 hours

    def get_data(self,**kwargs):
        from vidispine.vs_globalmetadata import VSGlobalMetadata
        from django.conf import settings
        md = VSGlobalMetadata(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                              user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD,
                              run_as=self.request.user.username)

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
                              user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD, run_as=self.request.user.username)

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
    from rest_framework.renderers import JSONRenderer, XMLRenderer, YAMLRenderer
    from rest_framework.permissions import IsAuthenticated

    permission_classes= (IsAuthenticated, )
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, XMLRenderer, YAMLRenderer)

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


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class AssetFolderCreatorView(APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer, XMLRenderer, YAMLRenderer
    from rest_framework.permissions import IsAuthenticated

    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes= (IsAuthenticated, )
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, XMLRenderer, YAMLRenderer)

    required_args = [
        'working_group_name',
        'commission_name',
        'user_name',
        'project_name',
        'project_id',
    ]

    required_settings = [
        'PLUTO_ASSET_FOLDER_BASEPATH',
        'WORKFLOW_EXEC_KEY',
        'WORKFLOW_EXEC_USER',
        'WORKFLOW_EXEC_HOSTS',
        'PLUTO_ASSETFOLDER_USER',
        'PLUTO_ASSETFOLDER_GROUP',
        'PROJECT_FILE_CREATION_SCRIPT_FINAL_OUTPUT'
    ]

    required_directories = [
    ]

    def __init__(self,*args,**kwargs):
        #super(self,AssetFolderCreatorView).__init__(*args,**kwargs)
        import re
        self.validation_expr = re.compile(r'[^\w\d]')

    def validate_field(self,value):
        return self.validation_expr.sub('_',value)

    def post(self, request):
        import os.path
        import re
        import subprocess
        from django.conf import settings

        self.required_directories.append(settings.PROJECT_FILE_CREATION_SCRIPT_FINAL_OUTPUT)
        #$base_path,$safe_working_group,$safe_commission,$safe_user."_".$safe_project
        for d in self.required_directories:
            if not os.path.isdir(d):
                return Response({'status': 'error', 'error': 'Server not configured properly, missing path {0}'.format(d)}, status=500)

        for a in self.required_settings:
            if not hasattr(settings,a):
                return Response({'status': 'error', 'error': 'Server not configured properly, missing {0}'.format(a)},status=500)

        for a in self.required_args:
            if not a in request.DATA:
                return Response({'status': 'error', 'error': 'You must specify {0}'.format(a)},status=400)

        if not re.match(r'^\w{2}-\d+$',request.DATA['project_id']):
            return Response({'status': 'error', 'error': 'Invalid vidispine ID: {0}'.format(request.DATA['project_id'])},status=400)

        #generate the actual asset folder path
        path = os.path.join(settings.PLUTO_ASSET_FOLDER_BASEPATH,
                            self.validate_field(request.DATA['working_group_name']),
                            self.validate_field(request.DATA['commission_name']),
                            "{0}_{1}".format(
                                self.validate_field(request.DATA['user_name']),
                                self.validate_field(request.DATA['project_name'])
                            )
                            )
        log.info("Built requested path {0} from {1}".format(path,str(request.DATA)))

        #send request to workflow server
        if isinstance(settings.WORKFLOW_EXEC_HOSTS, list):
            hosts = settings.WORKFLOW_EXEC_HOSTS
        else:
            hosts = [settings.WORKFLOW_EXEC_HOSTS]

        success=False
        helper = ""
        for rexec_host in hosts:
            remote_command = "/usr/local/bin/mkdir_on_behalf_of.pl \"{pathname}\" \"{username}\" \"{groupname}\"".format(
                pathname=path,
                groupname=settings.PLUTO_ASSETFOLDER_GROUP,
                username=settings.PLUTO_ASSETFOLDER_USER,
            )
            proc = subprocess.Popen([
                '/usr/bin/ssh',
                '-i',
                settings.WORKFLOW_EXEC_KEY,
                "{0}@{1}".format(settings.WORKFLOW_EXEC_USER,rexec_host),
                remote_command
            ],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            (command_stdout, command_stderr) = proc.communicate()
            if proc.returncode!=0:
                log.error("Error executing remote command on {0}: {1}".format(rexec_host,command_stderr))
            else:
                success=True
                helper = rexec_host
                break
        if not success:
            log.error("Unable to execute remote command on any host specified({0}). Aborting".format(settings.WORKFLOW_EXEC_HOSTS))
            return Response({'status': 'error', 'error': 'Internal command error'}, status=500)

        ptrfile = os.path.join(settings.PROJECT_FILE_CREATION_SCRIPT_FINAL_OUTPUT, str(request.DATA['project_id']) + '.ptr')
        log.info("Creating asset folder pointer at %s" % ptrfile)
        f = open(ptrfile,"w")
        f.writelines(path)
        f.close()
        log.info("Output asset folder location %s to %s" % (path, ptrfile))

        l = len(settings.PLUTO_ASSET_FOLDER_BASEPATH)
        rel_path = path[l:]
        if rel_path.startswith('/'):
            rel_path=rel_path[1:]

        return Response({'status': 'ok', 'asset_folder': rel_path, 'pointer_file': ptrfile,
                         'project': request.DATA['project_id'], 'helper': helper},status=200)