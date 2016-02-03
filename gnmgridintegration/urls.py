"""

"""
import logging

from django.conf.urls.defaults import *
from views import VSCallbackView
# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.gnmgridintegration.views.py. Inside that file is a class which responsedxs to the 
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.gnmgridintegration.views',
    url(r'^$', 'GenericAppView', kwargs={'template': 'gnmgridintegration/index.html'}, name='index'),
    url(r'^callback/jobnotification',VSCallbackView.as_view(), name='gridintegration_callback_url')
)
