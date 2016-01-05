from portal.generic.baseviews import ClassView
from django.views.generic import ListView
from django.http import HttpResponse
from django.shortcuts import render
from models import RestoreRequest

def index(request):
    return render(request,"gnmawsgr.html")


def r(request):
    from tasks import glacier_restore
    from datetime import datetime

    itemid = request.GET.get('id', '')

    print itemid

    path = request.GET.get('path', '')

    print path

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


class CurrentStatusView(ListView):
    model = RestoreRequest
    template_name = "gnmawsgr/restore_status.html"