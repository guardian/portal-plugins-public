from django.conf.urls.defaults import *
from views import GetStatsView, GetLibraryStats, ProjectScanReceiptView, ProjectStatInfoList, TotalSpaceByStorage, StorageCapacityView
from views import StorageDashMain, ProjectInfoGraphView,IndexView, ProjectStatusHistory, ProjectScanStats, ProjectInfoView
from views import ProjectUpdateReceiptView

urlpatterns = patterns('portal.plugins.gnmplutostats.views',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^stats/([^\/]+)\/*', GetStatsView.as_view(), name='gnmplutostats_get_stats'),
    url(r'^library_stats/([^\/]+)\/*', GetLibraryStats.as_view(), name='gnmplutostats_library_stats'),
    url(r'^storagedash/$', StorageDashMain.as_view(), name="plutostats_storage_dash"),
    url(r'^projectsize/receipts/', ProjectScanReceiptView.as_view(), name='projectsize_receipts'),
    url(r'^projectsize/all/', ProjectStatInfoList.as_view(), name='projectsize_all'),
    url(r'^projectsize/storage/(?P<storage_id>\w{2}-\d+)$', ProjectStatInfoList.as_view(), name='projectsize_storage'),
    url(r'^projectsize/storage/totals$', TotalSpaceByStorage.as_view(), name='projectsize_storage_totals'),
    url(r'^projectsize/project/graph$', ProjectInfoGraphView.as_view(), name='projectsize_graph'),
    url(r'^projectsize/receipt/stats$', ProjectScanStats.as_view(), name='projectscan_stats'),
    url(r'^project/(?P<project_id>\w{2}-\d+)/status_history$', ProjectStatusHistory.as_view(), name='projectstatus_history'),
    url(r'^project/(?P<project_id>\w{2}-\d+)/info$', ProjectInfoView.as_view(), name='projectinfo'),
    url(r'^project/(?P<project_id>\w{2}-\d+)/usage$', ProjectStatInfoList.as_view(), name='projectsize_project'),
    url(r'^project/(?P<project_id>\w{2}-\d+)/update$', ProjectUpdateReceiptView.as_view(), name='projectsize_update'),
    url(r'^system/storage/(?P<storage_id>\w{2}-\d+)$', StorageCapacityView.as_view(), name='system_storage_caps'),
)
