from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse_lazy
import views
from django.views.generic.simple import redirect_to

urlpatterns = patterns(
    'portal.plugins.gnmawsgr.views',
    url(r'^$', views.index, name="index"),
    # url(r'^r/$', views.r, name="request"),
    # url(r'^re/$', views.re, name="request_retry"),
    # url(r'^rc/$', views.rc, name="request_collection"),
    # url(r'^rcs/$', views.rcs, name="request_specific"),
    url(r'^restore/item$', views.RestoreItemRequestView.as_view(), name="request_item"),
    url(r'^restore/collection$', views.RestoreCollectionRequestView.as_view(), name="request_collection"),
    url(r'^restore/bulk/(\w{2}-\d+)', views.BulkRestoreStatusView.as_view(), name="bulk_status"),
    url(r'^projectinfo/(?P<projectid>\w{2}-\d+)', views.ProjectInfoView.as_view(), name="projectinfo"),
    url(r'^$', redirect_to, {'url': '/' }),
    url(r'^status$', views.CurrentStatusView.as_view(), name="status"),
    url(r'^status/$', redirect_to, {'url': reverse_lazy('status')}),
    url(r'^status/(?P<pk>.*)/delete$', views.DeleteRestoreRequest.as_view(), name="delete_request"),
)
