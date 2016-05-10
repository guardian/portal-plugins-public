"""

"""
import logging

from django.conf.urls.defaults import *
from views import BasicDataView,ItemInfoAPIView,AveragesRESTView
# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.gnmuploadprofiler.views.py. Inside that file is a class which responsedxs to the 
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.gnmuploadprofiler.views',
    url(r'^$', 'GenericAppView', kwargs={'template': 'gnmuploadprofiler/index.html'}, name='index'),
    url(r'^test/(\d{4}\d{2}\d{2})$', BasicDataView.as_view(), name='basic_data_specific'),
    url(r'^test/$', BasicDataView.as_view(), name='basic_data'),
    url(r'^averages/$', AveragesRESTView.as_view(), name='averages'),
    url(r'^iteminfo/(?P<itemid>\w{2}-\d+)$', ItemInfoAPIView.as_view(), name='item_info')
)
