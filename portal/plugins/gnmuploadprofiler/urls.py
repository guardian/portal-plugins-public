"""

"""
import logging

from django.conf.urls.defaults import *
from views import BasicDataView,ItemInfoAPIView,AveragesRESTView,ChartDataView
from django.views.generic import TemplateView

urlpatterns = patterns('portal.plugins.gnmuploadprofiler.views',
    url(r'^$', 'GenericAppView', kwargs={'template': 'gnmuploadprofiler/index.html'}, name='index'),
    url(r'^test/(\d{4}\d{2}\d{2})$', BasicDataView.as_view(), name='basic_data_specific'),
    url(r'^test/$', BasicDataView.as_view(), name='basic_data'),
    url(r'^averages/$', AveragesRESTView.as_view(), name='averages'),
    url(r'^chartdata/$', ChartDataView.as_view(), name='chartdata'),
    url(r'^ratio_chart$', TemplateView.as_view(template_name="gnmuploadprofiler/ratio_chart.html"), name='chart_view'),
    url(r'^iteminfo/(?P<itemid>\w{2}-\d+)$', ItemInfoAPIView.as_view(), name='item_info'),
)
