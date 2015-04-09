from portal.generic.baseviews import ClassView
from django.http import HttpResponse
from django.shortcuts import render
from forms import LogSearchForm

def index(request):
  #return HttpResponse(content="Hello world!",content_type="text/plain",status=200)
  form = LogSearchForm()
  return render(request,"logsearch.html", {'search_form': form })

