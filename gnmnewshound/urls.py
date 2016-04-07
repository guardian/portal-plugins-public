"""

"""
import logging

from django.conf.urls.defaults import *
from views import ByDateRangeView, GetVSClipView, TestPlayerView
# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.gnmnewshound.views.py. Inside that file is a class which responsedxs to the 
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.gnmnewshound.views',
    url(r'^$', 'GenericAppView', kwargs={'template': 'gnmnewshound/index.html'}, name='index'),
    url(r'^stories/date_range$', ByDateRangeView.as_view(), name='by_date_range'),
    url(r'^stories/(?P<category>\w+)/(?P<es_id>\w+)/vs', GetVSClipView.as_view(), name='get_vs_clip'),
    url(r'^stories/(?P<category>\w+)/(?P<es_id>[^\/]+)/preview', TestPlayerView.as_view(), name='test_player')
)
