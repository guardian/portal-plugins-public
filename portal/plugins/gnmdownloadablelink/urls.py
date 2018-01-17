"""

"""
import logging

from django.conf.urls.defaults import *
from views import LinksForItem, GetLink, CreateLinkRequest, ShapeTagList, RetryLinkRequest

urlpatterns = patterns('portal.plugins.gnmdownloadablelink.views',
    url(r'^api/links_for_item$', LinksForItem.as_view(), name="downloadable_links_for_item"),
    url(r'^api/link/(?P<pk>\d+)$', GetLink.as_view(), name="downloadable_link_item"),
    url(r'^api/new/(?P<item_id>\w{2}-\d+)/(?P<shape_tag>\w+)$', CreateLinkRequest.as_view(),name="downloadable_link_create"),
    url(r'^api/retry/(?P<pk>\d+)$', RetryLinkRequest.as_view(), name="downloadable_link_retry"),
    url(r'^api/shapetags$', ShapeTagList.as_view(), name="downloadable_link_shapetag"),
)
