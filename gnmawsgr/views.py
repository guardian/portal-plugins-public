from django.views.generic import ListView, DeleteView
from django.http import HttpResponse
from django.shortcuts import render
from models import RestoreRequest
from decorators import has_group
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy

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

    do_task = glacier_restore.delay(rq.pk,itemid,path)

    #print do_task

    return render(request,"r.html")

@login_required
@has_group('AWS_GR_Restore')
def ra(request):
    from tasks import glacier_restore
    from datetime import datetime

    # pprint(request.user.userprofile.__dict__)
    # pprint(request.user.groups.all())
    itemid = request.GET.get('id', '')
    path = request.GET.get('path', '')

    rq = RestoreRequest.objects.get(item_id=itemid)
    rq.status = "READY"
    rq.attempts = rq.attempts + 1
    rq.save()

    do_task = glacier_restore.delay(rq.pk,itemid,path)

    return


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