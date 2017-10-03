"""

"""
import logging

from django.conf.urls.defaults import patterns,url
from views import VSCallbackView, ConfigListView, MDEditView, MDDeleteView, MDCreateView, MDTestView, MDItemInfoView
from views import ProfileCreateView, ProfileDeleteView, ProfileEditView, ProfileListView, ProfileTestView
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy
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
    url(r'^admin/metadata/$', ConfigListView.as_view(), name='gnmgridintegration_admin_meta'),
    url(r'^admin/metadata$', RedirectView.as_view(url=reverse_lazy('gnmgridintegration_admin_meta'), permanent=True)),

    url(r'^admin/enable/new$', ProfileCreateView.as_view(), name='gnmgridintegration_new_profile'),
    url(r'^admin/enable/test/(?P<vs_item_id>\w{2}-\d+)/iteminfo$', MDItemInfoView.as_view(), name='gnmgridintegration_enable_item_meta'),
    url(r'^admin/enable/test/(?P<vs_item_id>\w{2}-\d+)$', ProfileTestView.as_view(), name='gnmgridintegation_test_profile'),
    url(r'^admin/enable/(?P<pk>\d+)/edit$', ProfileEditView.as_view(), name='gnmgridintegration_edit_profile'),
    url(r'^admin/enable/(?P<pk>\d+)/delete$', ProfileDeleteView.as_view(), name='gnmgridintegration_delete_profile'),
    url(r'^admin/enable/$', ProfileListView.as_view(), name='gnmgridintegration_admin_enable'),
    url(r'^admin/enable$', RedirectView.as_view(url=reverse_lazy('gnmgridintegration_admin_enable'), permanent=True)),
)
