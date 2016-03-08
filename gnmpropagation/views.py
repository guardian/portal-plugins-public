from django.shortcuts import render

def p(request):
    from tasks import propagate

    collectionid = request.GET.get('id', '')
    field = request.GET.get('field', '')
    switch = request.GET.get('switch', '')

    do_task = propagate.delay(collectionid,field,switch)

    return render(request,"p.html")
