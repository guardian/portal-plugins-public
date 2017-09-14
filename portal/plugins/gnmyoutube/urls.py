"""

"""
import logging

from django.conf.urls.defaults import *
from views import *

# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.portal.plugins.gnmyoutube.views.py. Inside that file is a class which responsedxs to the
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.portal.plugins.gnmyoutube.views',
    #url(r'^$', 'GenericAppView', kwargs={'template': 'portal.plugins.gnmyoutube/index.html'}, name='index'),
    url(r'^$', YoutubeIndexView.as_view(), name='index'),
    url(r'^admin/$',YoutubeAdminView.as_view(), name='admin'),
    url(r'^admin/testconnection$',YoutubeTestConnectionView.as_view(), name='testconn'),
    url(r'^action/([^\/]+)$',YoutubeTestAction.as_view(), name='actions'),
)
