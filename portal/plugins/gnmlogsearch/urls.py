from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to

urlpatterns = patterns(
    'portal.plugins.gnmlogsearch.views',
    url(r'^search', 'index'),
    url(r'^$', redirect_to, {'url': 'search/' })
)
