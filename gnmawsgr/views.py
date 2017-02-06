from django.views.generic import ListView, DeleteView
from django.http import HttpResponse
from django.shortcuts import render
from models import RestoreRequest, restore_request_for
from decorators import has_group
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from rest_framework.views import APIView, Response
from rest_framework.renderers import JSONRenderer
from rest_framework import permissions
from vsmixin import VSMixin, VSWrappedSearch
from utils import metadataValueInGroup
from portal.plugins.gnmawsgr import archive_test_value
from datetime import datetime

@login_required
def index(request):
    return render(request,"gnmawsgr.html")


class GenericRequestRestoreView(APIView):
    renderer_classes = (JSONRenderer,)
    
    @method_decorator(has_group('AWS_GR_Restore'))
    def dispatch(self, request, *args, **kwargs):
        return super(GenericRequestRestoreView,self).dispatch(request,*args,**kwargs)

    #if restore request status is any of these, then proceed with the restore
    should_restore_statuses = [
        "READY", "FAILED", "NOT_GLACIER", "COMPLETED", "RETRY"
    ]
    
    def request_item_restore(self, itemid, itemdata, parent_project=None, rqstatus="READY"):
        from tasks import glacier_restore
        path = metadataValueInGroup('ExternalArchiveRequest', 'gnm_external_archive_external_archive_path',
                                    itemdata['item'])

        rq = restore_request_for(itemid, username=self.request.user.username, parent_project=parent_project, rqstatus=rqstatus)
        
        if rq.status in self.should_restore_statuses:
            do_task = glacier_restore.delay(rq.pk, itemid, path)
        else:
            do_task = None
            
        return (rq,do_task)
    
    def get_item_data(self,itemid):
        from portal.vidispine.igeneral import performVSAPICall
        from portal.vidispine.iitem import ItemHelper
        ith = ItemHelper()
        res = performVSAPICall(func=ith.getItemMetadata,
                               args={'item_id': itemid},
                               vsapierror_templateorcode='template.html')
    
        return res['response']
    
    def make_response(self, requesttuple):
        return {
            "status": "ok",
            "request_id": requesttuple[0].pk,
            "request_attempt": requesttuple[0].attempts,
            "task_id": requesttuple[1]
        }
    
    
class RestoreItemRequestView(GenericRequestRestoreView):
    def get(self, request):
        from traceback import format_exc
        try:
            if 'id' in request.GET:
                itemid = request.GET['itemid']
            else:
                return Response({'status': "error", "error": "Need an item id"}, status=400)

            if 'retry' in request.GET:
                should_status = "RETRY"
            else:
                should_status = "READY"

            itemdata = self.get_item_data(itemid)

            return Response(
                self.make_response(self.request_item_restore(itemid, itemdata, should_status))
            )
        
        except Exception as e:
            return Response({"status": "error", "error": str(e), "trace": format_exc()}, status=500)
    

class RestoreCollectionRequestView(GenericRequestRestoreView):
    def get(self, request):
        from traceback import format_exc
        try:
            from bulk_restorer import BulkRestorer
            r = BulkRestorer()
            
            if not 'id' in request.GET:
                return Response({'status': 'error', 'detail': "Need an item ID"},status=400)
            
            if 'selected' in request.GET:
                selection_list = request.GET['selected'].split(",")
            else:
                selection_list = None
                
            job_id = r.initiate_bulk(request.user,request.GET['id'],selection=selection_list)
            
            return Response(
                {
                    "status": "ok",
                    "bulk_restore_request": job_id
                }
            )
        except Exception as e:
            return Response({"status": "error", "error": str(e), "trace": format_exc()}, status=500)
        

class CurrentStatusView(ListView):
    model = RestoreRequest
    template_name = "gnmawsgr/restore_status.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CurrentStatusView,self).dispatch(request,*args,**kwargs)


class DeleteRestoreRequest(DeleteView):
    model = RestoreRequest
    template_name = "gnmawsgr/restore_request_delete.html"
    success_url = reverse_lazy('status')

    @method_decorator(permission_required('delete_restorerequest', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteRestoreRequest,self).dispatch(request,*args,**kwargs)


class ProjectInfoView(APIView):
    renderer_classes = (JSONRenderer, )
    permission_classes = (permissions.IsAuthenticated, )
    
    def get(self, request, projectid=None):
        """
        Returns information about the project's archive status.  This is used to determine whether to show restore controls or not.
        :param request: django request object
        :param projectid: project id as given by Vidispine
        :return: HttpResponse with a json object for ajax
        """
        import traceback
        import time

        try:
            promises = {
                'total_items': VSWrappedSearch({'__collection': projectid}).execute(),
                'archived_items': VSWrappedSearch(
                    {'__collection': projectid, 'gnm_asset_status': "Archived to External"}).execute(),
                'restored_items': VSWrappedSearch(
                    {'__collection': projectid, 'gnm_asset_status': "Ready for Editing (from Archive)"}
                ).execute(),
                'waiting_items': VSWrappedSearch(
                    {'__collection': projectid, 'gnm_asset_status': "Waiting for Archive Restore"}
                ).execute()
            }
            
            results = dict(
                map(lambda (key, promise): (key, promise.waitfor_json()), promises.items())
            )
            
            return Response({'status': "ok", "results": dict(map(lambda (key,searchresult): (key, searchresult['hits']), results.items()))})
        except Exception as e:
            traceback.print_exc()
            return Response({'status': "error", "detail": str(e)},status=500)
        
        
class BulkRestoreStatusView(APIView):
    renderer_classes = (JSONRenderer, )
    permission_classes = (permissions.IsAuthenticated, )
    
    def get(self, request, vsid):
        """
        Returns information about the current state of the bulk restore request, so long as the requesting user
        is an admin or the owner of the request.
        :param request: Django request object
        :param pk: primary key of a bulk restore request
        :return: json response of information
        """
        from models import BulkRestore
        from serializers import BulkRestoreSerializer
        try:
            bulk_request = BulkRestore.objects.get(parent_collection=vsid)
            s = BulkRestoreSerializer(bulk_request, many=False)
            if request.user.is_superuser or bulk_request.username == request.user.name:
                return Response(s.data)
            else:
                raise BulkRestore.DoesNotExist  #default behaviour, mask the auth error by returning 404
        except BulkRestore.DoesNotExist:
            return Response({'status': 'error'},status=404)
        