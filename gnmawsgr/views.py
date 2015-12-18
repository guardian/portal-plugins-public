from portal.generic.baseviews import ClassView
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request,"gnmawsgr.html")

def r(request):

    from tasks import glacier_restore

    do_task = glacier_restore.delay(1,1)

    print do_task

    return render(request,"r.html")


