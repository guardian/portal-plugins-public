from django.conf.urls.defaults import patterns, url
from portal.plugins.gnmawsgr import views
from django.views.generic.simple import redirect_to

urlpatterns = patterns(
    'portal.plugins.gnmawsgr.views',
    url(r'^', views.index),
    url(r'^$', redirect_to, {'url': '/' }),
)
