"""

"""
import logging

from django.conf.urls.defaults import *
from views import GetStatsView, GetLibraryStats
# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.portal.plugins.gnmplutostats.views.py. Inside that file is a class which responsedxs to the
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.portal.plugins.gnmplutostats.views',
    url(r'^$', 'GenericAppView', kwargs={'template': 'portal.plugins.gnmplutostats/index.html'}, name='index'),
    url(r'^stats/([^\/]+)\/*', GetStatsView.as_view(), name='gnmplutostats_get_stats'),
    url(r'^library_stats/([^\/]+)\/*', GetLibraryStats.as_view(), name='gnmplutostats_library_stats'),
)
