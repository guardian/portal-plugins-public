from django.conf.urls.defaults import patterns, url
from portal.plugins.gnmzeitgeist import views
from django.views.generic.simple import redirect_to

urlpatterns = patterns(
    'portal.plugins.portal.plugins.gnmzeitgeist.views',
    url(r'^data/*$', views.data),
    url(r'^$', views.index),
    url(r'^datasource/add$', views.add_data_source)
    #url(r'^$', redirect_to, {'url': 'hello/' })
)
