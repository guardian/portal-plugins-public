from django.conf.urls.defaults import patterns, url
from portal.plugins.gnmsyndication import views
from django.views.generic.simple import redirect_to

urlpatterns = patterns(
    'portal.plugins.gnmsyndication.views',
    url(r'^stats/data/platforms_by_day$', views.platforms_by_day),
    url(r'^stats/assets_by_day/(\d{1,2}/\d{1,2}/\d{4})$', views.assets_by_day),
    url(r'^stats/report/csv$', views.csv_report, name="gnmsyndication_csv_report"),
    url(r'^stats/$', views.index),
    url(r'^stats$', redirect_to, {'url': 'stats/'}),
    url(r'^admin/*$', views.AdminPlatformsList.as_view(), name="admin"),
    url(r'^admin/platform/new$', views.AdminPlatformCreate.as_view(), name='platform_create'),
    url(r'^admin/platform/(?P<pk>\d+)/edit$', views.AdminPlatformUpdate.as_view(), name='platform_update'),
    url(r'^admin/platform/(?P<pk>\d+)/delete$', views.AdminPlatformDelete.as_view(), name='platform_delete'),
    url(r'^$', redirect_to, {'url': 'stats/' }),
)
