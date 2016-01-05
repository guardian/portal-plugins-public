from django.views.generic import ListView
from django.http import HttpResponse
from django.shortcuts import render
from models import RestoreRequest
from decorators import has_group
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

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
        rq.username = "????"
        rq.status = "READY"
        rq.attempts = 0
        rq.item_id = itemid
        rq.save()

    do_task = glacier_restore.delay(rq.pk,itemid,path)

    #print do_task

    return render(request,"r.html")

@login_required
class CurrentStatusView(ListView):
    model = RestoreRequest
    template_name = "gnmawsgr/restore_status.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CurrentStatusView,self).dispatch(request,*args,**kwargs)