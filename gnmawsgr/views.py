from django.views.generic import ListView, DeleteView
from django.http import HttpResponse
from django.shortcuts import render
from models import RestoreRequest
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

        try:
            rq = RestoreRequest.objects.get(item_id=itemid)
            if rqstatus=="RETRY":
                rq.status = "RETRY"
                rq.save()
        except RestoreRequest.DoesNotExist:
            rq = RestoreRequest()
            rq.requested_at = datetime.now()
            rq.username = self.request.user.username
            rq.parent_collection = parent_project
            rq.status = rqstatus
            rq.attempts = 1
            rq.item_id = itemid
            rq.save()
        
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
            from portal.vidispine.icollection import CollectionHelper
            from portal.vidispine.igeneral import performVSAPICall
            if 'id' in request.GET:
                collid = request.GET['id']
            else:
                return Response({'status': "error", "error": "Need a collection id"}, status=400)

            ch = CollectionHelper()
            res = performVSAPICall(func=ch.getCollection,
                                   args={'collection_id': collid},
                                   vsapierror_templateorcode='template.html')
            collection = res['response']
                
            if 'selected' in request.GET:
                to_restore_list = request.GET['selected'].split(",")
            else:
                to_restore_list = collection.getItems()
                
            responses = map(lambda itemdata: self.make_response(self.request_item_restore(itemdata.getId(), itemdata, parent_project=collection.getId())), to_restore_list)
            
            return Response(
                {
                    "status": "ok",
                    "count": len(responses),
                    "responses": responses
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
                    {'__collection': projectid, 'gnm_external_archive_external_archive_status': "Archived"}).execute()
            }
            
            results = dict(
                map(lambda (key, promise): (key, promise.waitfor_json()), promises.items())
            )
            
            return Response({'status': "ok", "results": dict(map(lambda (key,searchresult): (key, searchresult['hits']), results.items()))})
        except Exception as e:
            traceback.print_exc()
            return Response({'status': "error", "detail": str(e)},status=500)