import logging

from django.conf.urls.defaults import patterns, url
from views import ConfigAlertsView, AlertsEditView, AlertsDeleteView, AlertsCreateView, StorageDataList, StorageDataAdd, StorageDataUpdate
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy


urlpatterns = patterns('portal.plugins.gnmpagerduty.views',
    url(r'^$', 'GenericAppView', kwargs={'template': 'gnmpagerduty/index.html'}, name='index'),
    url(r'^alerts/$', ConfigAlertsView.as_view(), name='gnmpagerduty_admin_alerts'),
    url(r'^edit/$', AlertsEditView.as_view(), name='gnmpagerduty_edit'),
    url(r'^storagedata/$', StorageDataList.as_view()),
    url(r'^storagedata/new$', StorageDataAdd.as_view(), name="gnmpagerduty_storage_add"),
    url(r'^storagedata/update$', StorageDataUpdate.as_view(), name="gnmpagerduty_storage_update"),
)
