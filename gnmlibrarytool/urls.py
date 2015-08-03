"""

"""
import logging
from .views import MainAppView, LibraryListView
from django.conf.urls.defaults import patterns, url

# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.gnmlibrarytool.views.py. Inside that file is a class which responsedxs to the 
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.gnmlibrarytool.views',
    url(r'^$', MainAppView.as_view(), name='index'),
    url(r'^endpoint/list$', LibraryListView.as_view(), name='list_api'),
)