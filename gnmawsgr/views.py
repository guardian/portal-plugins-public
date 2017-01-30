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

@login_required
def index(request):
    return render(request,"gnmawsgr.html")

@login_required
@has_group('AWS_GR_Restore')
def r(request):
    from tasks import glacier_restore
    from datetime import datetime
    from portal.vidispine.igeneral import performVSAPICall
    from portal.vidispine.iitem import ItemHelper

    itemid = request.GET.get('id', '')
    ith = ItemHelper()
    res = performVSAPICall(func=ith.getItemMetadata, \
                                    args={'item_id':itemid}, \
                                    vsapierror_templateorcode='template.html')

    itemdata = res['response']

    path = metadataValueInGroup('ExternalArchiveRequest','gnm_external_archive_external_archive_path',itemdata['item'])

    try:
        rq = RestoreRequest.objects.get(item_id=itemid)
    except RestoreRequest.DoesNotExist:
        rq = RestoreRequest()
        rq.requested_at = datetime.now()
        rq.username = request.user.username
        rq.status = "READY"
        rq.attempts = 1
        rq.item_id = itemid
        rq.save()

    if (rq.status == "READY") or (rq.status == "FAILED") or (rq.status == "NOT_GLACIER") or (rq.status == "COMPLETED"):
        do_task = glacier_restore.delay(rq.pk,itemid,path)
        return render(request,"restore.html")
    else:
        if (rq.requested_at == '') or (rq.username == '') or (rq.status == ''):
            return render(request,"do_not_restore_no_data.html")
        else:
            return render(request,"do_not_restore.html", {"at": rq.requested_at, "user": rq.username, "status": rq.status})


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

@login_required
@has_group('AWS_GR_Restore')
def re(request):
    from tasks import glacier_restore
    from portal.vidispine.igeneral import performVSAPICall
    from portal.vidispine.iitem import ItemHelper

    itemid = request.GET.get('id', '')

    ith = ItemHelper()

    res = performVSAPICall(func=ith.getItemMetadata, \
                                    args={'item_id':itemid}, \
                                    vsapierror_templateorcode='template.html')

    itemdata = res['response']

    path = metadataValueInGroup('ExternalArchiveRequest','gnm_external_archive_external_archive_path',itemdata['item'])

    rq = RestoreRequest.objects.get(item_id=itemid)
    rq.status = "RETRY"
    rq.attempts = rq.attempts + 1
    rq.save()
    do_task = glacier_restore.delay(rq.pk,itemid,path)
    return render(request,"restore.html")

@login_required
@has_group('AWS_GR_Restore')
def rc(request):
    from tasks import glacier_restore
    from datetime import datetime
    from portal.vidispine.icollection import CollectionHelper
    from portal.vidispine.igeneral import performVSAPICall
    from portal.vidispine.iitem import ItemHelper

    collid = request.GET.get('id', '')
    ch = CollectionHelper()
    res = performVSAPICall(func=ch.getCollection, \
                                args={'collection_id':collid}, \
                                vsapierror_templateorcode='template.html')
    collection = res['response']
    content = collection.getItems()

    for data in content:
        ith = ItemHelper()
        itemid = data.getId()
        res2 = performVSAPICall(func=ith.getItemMetadata, \
                                    args={'item_id':itemid}, \
                                    vsapierror_templateorcode='template.html')
        itemdata = res2['response']

        test_value = metadataValueInGroup('ExternalArchiveRequest','gnm_external_archive_external_archive_status',itemdata['item'])
        if test_value == archive_test_value:
            path = metadataValueInGroup('ExternalArchiveRequest','gnm_external_archive_external_archive_path',itemdata['item'])

            try:
                rq = RestoreRequest.objects.get(item_id=itemid)
            except RestoreRequest.DoesNotExist:
                rq = RestoreRequest()
                rq.requested_at = datetime.now()
                rq.username = request.user.username
                rq.status = "READY"
                rq.attempts = 1
                rq.item_id = itemid
                rq.parent_collection = collid
                rq.save()

            if (rq.status == "READY") or (rq.status == "FAILED") or (rq.status == "NOT_GLACIER") or (rq.status == "COMPLETED"):
                do_task = glacier_restore.delay(rq.pk,itemid,path)

    return render(request,"restore_collection.html")

@login_required
@has_group('AWS_GR_Restore')
def rcs(request):
    from tasks import glacier_restore
    from datetime import datetime
    from portal.vidispine.icollection import CollectionHelper
    from portal.vidispine.igeneral import performVSAPICall
    from portal.vidispine.iitem import ItemHelper

    collid = request.GET.get('id', '')

    selected = request.GET.get('selected', '')

    selectedready = selected.split(",")

    ch = CollectionHelper()

    res = performVSAPICall(func=ch.getCollection, \
                                args={'collection_id':collid}, \
                                vsapierror_templateorcode='template.html')

    collection = res['response']

    content = collection.getItems()

    for data in content:

        ith = ItemHelper()

        itemid = data.getId()

        res2 = performVSAPICall(func=ith.getItemMetadata, \
                                    args={'item_id':itemid}, \
                                    vsapierror_templateorcode='template.html')

        itemdata = res2['response']

        try:
            test_value = metadataValueInGroup('ExternalArchiveRequest','gnm_external_archive_external_archive_status',itemdata['item'])
        except:
            print 'An error broke the call'

        if (test_value == archive_test_value) and itemid in selectedready:

            try:
                path = metadataValueInGroup('ExternalArchiveRequest','gnm_external_archive_external_archive_path',itemdata['item'])
            except:
                print 'An error broke the call'

            try:
                rq = RestoreRequest.objects.get(item_id=itemid)
            except RestoreRequest.DoesNotExist:
                rq = RestoreRequest()
                rq.requested_at = datetime.now()
                rq.username = request.user.username
                rq.status = "READY"
                rq.attempts = 1
                rq.item_id = itemid
                rq.parent_collection = collid
                rq.save()

            if (rq.status == "READY") or (rq.status == "FAILED") or (rq.status == "NOT_GLACIER") or (rq.status == "COMPLETED"):
                do_task = glacier_restore.delay(rq.pk,itemid,path)

    return render(request,"restore_selected.html")


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