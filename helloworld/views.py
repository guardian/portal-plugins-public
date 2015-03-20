from portal.generic.baseviews import ClassView
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
  #return HttpResponse(content="Hello world!",content_type="text/plain",status=200)
  return render(request,"helloworld.html")

