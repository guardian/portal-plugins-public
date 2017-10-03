"""
This is where you can write a lot of the code that responds to URLS - such as a page request from a browser
or a HTTP request from another application.

From here you can follow the Cantemo Portal Developers documentation for specific code, or for generic 
framework code refer to the Django developers documentation. 

"""
import logging

from django.contrib.auth.decorators import login_required
from portal.generic.baseviews import ClassView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required, login_required
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy
from portal.vidispine.iitem import ItemHelper
from portal.vidispine.iexception import NotFoundError
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from models import GridMetadataFields, GridCapturePreset
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


### Views for Vidispine callback
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
        #pprint(request.DATA)
        get_new_thumbnail(request.DATA)
        return Response({'status': 'ok'}, status=200)
        # except TypeError as e:
        #     return Response({'status': 'error', 'exception': str(e)},status=400)


### Views for admin metadata editor
class ConfigListView(ListView):
    @method_decorator(permission_required('change_gridmetadatafields', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ConfigListView,self).dispatch(request,*args,**kwargs)
    model = GridMetadataFields
    template_name = "gnmgridintegration/admin_list.html"


class MDEditView(UpdateView):
    @method_decorator(permission_required('change_gridmetadatafields', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(MDEditView,self).dispatch(request,*args,**kwargs)
    model = GridMetadataFields
    template_name = "gnmgridintegration/meta_edit.html"
    success_url = reverse_lazy('gnmgridintegration_admin_meta')


class MDDeleteView(DeleteView):
    @method_decorator(permission_required('delete_gridmetadatafields', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(MDDeleteView,self).dispatch(request,*args,**kwargs)
    model = GridMetadataFields
    template_name = "gnmgridintegration/meta_delete.html"
    success_url = reverse_lazy('gnmgridintegration_admin_meta')


class MDCreateView(CreateView):
    @method_decorator(permission_required('create_gridmetadatafields', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(MDCreateView,self).dispatch(request,*args,**kwargs)
    model = GridMetadataFields
    template_name = "gnmgridintegration/meta_edit.html"
    success_url = reverse_lazy('gnmgridintegration_admin_meta')


class MDTestView(APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer
    from rest_framework import permissions

    permission_classes = (permissions.IsAdminUser, )
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    def get(self, request, vs_item_id=None):
        from django.conf import settings
        from gnmvidispine.vs_item import VSItem, VSNotFound
        from models import GridMetadataFields
        from traceback import format_exc
        from notification_handler import do_meta_substitution, vs_field_list
        item = VSItem(url=settings.VIDISPINE_URL, port=settings.VIDISPINE_PORT,
              user=settings.VIDISPINE_USERNAME, passwd=settings.VIDISPINE_PASSWORD,run_as=request.user.username)

        try:
            #log.debug("Looking up item {0}".format(vs_item_id))
            fieldnames = vs_field_list()
            #log.debug("Field list: {0}".format(fieldnames))
            try:
                item.populate(vs_item_id, specificFields=fieldnames)
            except VSNotFound as e:
                return Response({'status': 'error', 'problem': 'Item not found', 'exception': e}, status=404)

            return Response({'status': 'success',
                             'item_meta': do_meta_substitution(item, -1, 1),
                             'rights_meta': do_meta_substitution(item, -1, 2)})

        except Exception as e:
            if settings.DEBUG:
                return Response({'status': 'error', 'exception': e, 'type': e.__class__, 'trace': format_exc()}, status=500)
            else:
                return Response({'status': 'error', 'exception': e, }, status=500)


class MDItemInfoView(APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer
    from rest_framework import permissions

    permission_classes = (permissions.IsAdminUser, )
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    interesting_fields = ['title', 'gnm_type', 'gnm_asset_category', 'representativeThumbnailNoAuth']

    def get(self, request, vs_item_id=None):
        from django.conf import settings
        from gnmvidispine.vs_item import VSItem, VSNotFound
        from notification_handler import VIDISPINE_GRID_REF_FIELD
        from notification_handler import vs_field_list
        from pprint import pformat
        #log.debug("Request data: {0}".format(pformat(request.__dict__)))
        #log.debug("Request user: {0}".format(request.user))

        item = VSItem(url=settings.VIDISPINE_URL, port=settings.VIDISPINE_PORT,
              user=settings.VIDISPINE_USERNAME, passwd=settings.VIDISPINE_PASSWORD,run_as=request.user.username)

        try:
            #log.debug("Looking up item {0}".format(vs_item_id))
            item.populate(vs_item_id, specificFields = self.interesting_fields)
        except VSNotFound as e:
            return Response({'status': 'error', 'problem': 'Item not found', 'exception': e}, status=404)
        meta = {}

        for f in self.interesting_fields:
            meta[f] = item.get(f, allowArray=True)
        for f in vs_field_list():
            meta[f] = item.get(f, allowArray=True)
        gridrefs = item.get(VIDISPINE_GRID_REF_FIELD, allowArray=True)
        if not isinstance(gridrefs,list):
            gridrefs=[gridrefs]
        meta[VIDISPINE_GRID_REF_FIELD] = gridrefs
        return Response({'status': 'success', 'item': vs_item_id, 'metadata': meta})

### Views for admin enable profile editor
class ProfileListView(ListView):
    @method_decorator(permission_required('change_gridcapturepreset', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileListView,self).dispatch(request,*args,**kwargs)
    model = GridCapturePreset
    template_name = "gnmgridintegration/admin_enable_disable.html"


class ProfileEditView(UpdateView):
    @method_decorator(permission_required('change_gridcapturepreset', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileEditView,self).dispatch(request,*args,**kwargs)

    model = GridCapturePreset
    template_name = "gnmgridintegration/profile_edit.html"
    success_url = reverse_lazy('gnmgridintegration_admin_enable')


class ProfileDeleteView(DeleteView):
    @method_decorator(permission_required('delete_gridcapturepreset', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileDeleteView,self).dispatch(request,*args,**kwargs)
    model = GridCapturePreset
    template_name = "gnmgridintegration/profile_delete.html"
    success_url = reverse_lazy('gnmgridintegration_admin_enable')


class ProfileCreateView(CreateView):
    @method_decorator(permission_required('create_gridcapturepreset', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileCreateView,self).dispatch(request,*args,**kwargs)

    model = GridCapturePreset
    template_name = "gnmgridintegration/profile_edit.html"
    success_url = reverse_lazy('gnmgridintegration_admin_enable')


class ProfileTestView(APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer
    from rest_framework import permissions

    permission_classes = (permissions.IsAdminUser, )
    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    def get(self, request, vs_item_id=None):
        from django.conf import settings
        from gnmvidispine.vs_item import VSItem, VSNotFound, VSException
        from traceback import format_exc
        from models import GridCapturePreset
        from traceback import format_exc
        from notification_handler import should_trigger, vs_field_list

        item = VSItem(url=settings.VIDISPINE_URL, port=settings.VIDISPINE_PORT,
              user=settings.VIDISPINE_USERNAME, passwd=settings.VIDISPINE_PASSWORD,run_as=request.user.username)

        try:
            item.populate(vs_item_id, specificFields=vs_field_list())
            n=should_trigger(item)
            if n:
                ps = GridCapturePreset.objects.get(pk=n)
                return Response({'status': 'ok', 'result': True, 'because': ps.info()})
            else:
                return Response({'status': 'ok', 'result': False})
        except VSNotFound as e:
            return Response({'status': 'error', 'exception': 'Vidispine item {0} not found'.format(vs_item_id)},status=404)
        except VSException as e:
            return Response({'status': 'error', 'exception': 'Vidispine error {0}'.format(e.__class__.__name__),
                             'detail': {
                                 'type': e.exceptionType,
                                 'context': e.exceptionContext,
                                 'what': e.exceptionWhat,
                                 'id': e.exceptionID
                             }}, status=500)
        except Exception as e:
            return Response({'status': 'error', 'exception': unicode(e), 'trace': format_exc()}, status=500)