"""

"""
import logging

from django.conf.urls.defaults import patterns,url
from views import VSCallbackView, ConfigListView, MDEditView, MDDeleteView, MDCreateView, MDTestView, MDItemInfoView
# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.gnmgridintegration.views.py. Inside that file is a class which responsedxs to the 
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.gnmgridintegration.views',
    url(r'^$', 'GenericAppView', kwargs={'template': 'gnmgridintegration/index.html'}, name='index'),
    url(r'^callback/jobnotification$',VSCallbackView.as_view(), name='gridintegration_callback_url'),
    url(r'^admin/metadata/(?P<pk>\d+)/edit$', MDEditView.as_view(), name='gnmgridintegration_edit_meta'),
    url(r'^admin/metadata/(?P<pk>\d+)/delete$', MDDeleteView.as_view(), name='gnmgridintegration_delete_meta'),
    url(r'^admin/metadata/new$', MDCreateView.as_view(), name='gnmgridintegration_new_meta'),
    url(r'^admin/metadata/test/(?P<vs_item_id>\w{2}-\d+)/iteminfo$', MDItemInfoView.as_view(), name='gnmgridintegration_item_meta'),
    url(r'^admin/metadata/test/(?P<vs_item_id>\w{2}-\d+)$', MDTestView.as_view(), name='gnmgridintegration_test_meta'),
    url(r'^admin/metadata/*$', ConfigListView.as_view(), name='gnmgridintegration_admin_meta'),
)
