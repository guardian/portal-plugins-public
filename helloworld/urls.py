from django.conf.urls.defaults import patterns, url
from portal.plugins.helloworld import views
from django.views.generic.simple import redirect_to

urlpatterns = patterns(
    'portal.plugins.helloworld.views',
    url(r'^hello', views.index),
    url(r'^$', redirect_to, {'url': 'hello/' })
)
