from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse_lazy
import views
from django.views.generic.simple import redirect_to

urlpatterns = patterns(
    'portal.plugins.gnmawsgr.views',
    url(r'^$', views.index, name="index"),
    url(r'^r/$', views.r, name="request"),
    url(r'^ra/$', views.ra, name="request"),
    url(r'^$', redirect_to, {'url': '/' }),
    url(r'^status$', views.CurrentStatusView.as_view(), name="status"),
    url(r'^status/$', redirect_to, {'url': reverse_lazy('status')}),
    url(r'^status/(?P<pk>.*)/delete$', views.DeleteRestoreRequest.as_view(), name="delete_request"),
)
