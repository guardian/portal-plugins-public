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