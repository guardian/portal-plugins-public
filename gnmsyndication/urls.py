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
    url(r'^$', redirect_to, {'url': 'stats/' }),
)
