"""

"""
import logging

from django.conf.urls.defaults import *
from views import LinksForItem, GetLink, CreateLinkRequest
# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.gnmdownloadablelink.views.py. Inside that file is a class which responsedxs to the 
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.gnmdownloadablelink.views',
    url(r'^api/links_for_item$', LinksForItem.as_view(), name="downloadable_links_for_item"),
    url(r'^api/link/(?P<pk>\d+)$', GetLink.as_view(), name="downloadable_link_item"),
    url(r'^api/new/(?P<item_id>\w{2}-\d+)/(?P<shape_tag>\w+)', CreateLinkRequest.as_view()),
)
