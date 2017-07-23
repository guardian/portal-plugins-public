from django.conf.urls.defaults import patterns, url
from django.conf.urls import include

urlpatterns = [
    url(r'^gnmlibrarytool/',include('gnmlibrarytool.urls', namespace='gnmlibrarytool'))
    ]