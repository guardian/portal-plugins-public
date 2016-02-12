from django.views.generic import ListView, DeleteView
from django.http import HttpResponse
from django.shortcuts import render
from models import RestoreRequest
from decorators import has_group
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy

archive_test_value = 'Archived'

@login_required
def index(request):
    return render(request,"gnmawsgr.html")

@login_required
@has_group('AWS_GR_Restore')
def r(request):
    from tasks import glacier_restore
    from datetime import datetime

    # pprint(request.user.userprofile.__dict__)
    # pprint(request.user.groups.all())
    itemid = request.GET.get('id', '')
    path = request.GET.get('path', '')

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
        #print do_task
        return render(request,"r.html")
    else:
        return render(request,"no.html", {"at": rq.requested_at, "user": rq.username, "status": rq.status})

def p(request):
    from tasks import propagate

    collectionid = request.GET.get('id', '')
    field = request.GET.get('field', '')
    switch = request.GET.get('switch', '')

    do_task = propagate.delay(collectionid,field,switch)

    return render(request,"p.html")


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

    itemid = request.GET.get('id', '')
    path = request.GET.get('path', '')

    rq = RestoreRequest.objects.get(item_id=itemid)
    rq.status = "RETRY"
    rq.attempts = rq.attempts + 1
    rq.save()
    do_task = glacier_restore.delay(rq.pk,itemid,path)
    return render(request,"r.html")

def _find_group(groupname,meta):
    if not 'group' in meta:
        return None

    for g in meta['group']:
        if g['name'] == groupname:
            return g
        _find_group(groupname,g)

def metadataValueInGroup(groupname, mdkey, meta):
    for item_data in meta:
        for ts in item_data['metadata']['timespan']:
            group = _find_group(groupname, ts)
            if group is None:
                raise ValueError("Could not find group {0}".format(groupname))
            for f in group['field']:
                if f['name'] == mdkey:
                    rtn = map(lambda x: x['value'],f['value'])
                    if len(rtn)==1:
                        return rtn[0]
                    else:
                        return rtn
    raise ValueError("Could not find metadata key {0}".format(mdkey))

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

        try:
            test_value = metadataValueInGroup('ExternalArchiveRequest','gnm_external_archive_external_archive_status',itemdata['item'])
        except:
            print 'An error broke the call'

        if test_value == archive_test_value:

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

    return render(request,"rc.html")
