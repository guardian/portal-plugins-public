from django.conf.urls.defaults import patterns, url
from views import ConfigAlertsView, StorageDataList, StorageDataAdd, StorageDataUpdate

urlpatterns = patterns('portal.plugins.gnmpagerduty.views',
    url(r'^$', 'GenericAppView', kwargs={'template': 'gnmpagerduty/index.html'}, name='index'),
    url(r'^alerts/$', ConfigAlertsView.as_view(), name='gnmpagerduty_admin_alerts'),
    url(r'^storagedata/$', StorageDataList.as_view()),
    url(r'^storagedata/new$', StorageDataAdd.as_view(), name="gnmpagerduty_storage_add"),
    url(r'^storagedata/update$', StorageDataUpdate.as_view(), name="gnmpagerduty_storage_update"),
)
