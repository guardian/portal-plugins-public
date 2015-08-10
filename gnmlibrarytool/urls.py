"""

"""
import logging
from django.contrib.auth.decorators import login_required,permission_required
from .views import MainAppView, LibraryListView, CreateLibraryView, DeleteLibraryView, SaveStorageRuleView, \
    DeleteStorageRuleView
from django.conf.urls.defaults import patterns, url

# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.gnmlibrarytool.views.py. Inside that file is a class which responsedxs to the 
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.gnmlibrarytool.views',
    url(r'^$', login_required(MainAppView.as_view()), name='index'),
    url(r'^(?P<lib>\w{2}[\-\*]\d+)$', login_required(MainAppView.as_view()), name='libtool_editor'),
    url(r'^endpoint/new$', login_required(CreateLibraryView.as_view()), name='libtool_new'),
    url(r'^endpoint/list$', login_required(LibraryListView.as_view()), name='libtool_list_api'),
    url(r'^endpoint/delete$', login_required(DeleteLibraryView.as_view()), name='libtool_delete'),
    url(r'^endpoint/savestorage$', login_required(SaveStorageRuleView.as_view()), name="libtool_savestorage"),
    url(r'^endpoint/deletestorage$', login_required(DeleteStorageRuleView.as_view()), name="libtool_deletestorage"),
)