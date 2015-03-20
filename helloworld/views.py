from django.http import HttpResponse

def index(request):
  return HttpResponse(content="Hello world!",content_type="text/plain",status=200)

