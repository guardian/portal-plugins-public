"""

"""
import logging

from django.conf.urls.defaults import *
from views import MessageListView
# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.gnmkinesisresponder.views.py. Inside that file is a class which responsedxs to the 
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.kinesisresponder.views',
    url(r'^messages/(?P<stream_name>\w+)/$', MessageListView.as_view(), name='message_list_view')
)
