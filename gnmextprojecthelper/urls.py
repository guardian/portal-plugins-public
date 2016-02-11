"""

"""
import logging

from django.conf.urls.defaults import *
from views import ProjectTemplateFileView,ProjectDefaultInformationView
# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.gnmextprojecthelper.views.py. Inside that file is a class which responsedxs to the 
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.gnmextprojecthelper.views',
    url(r'^$', 'GenericAppView', kwargs={'template': 'gnmextprojecthelper/index.html'}, name='index'),
    url(r'^get_template/(?P<project_type>[A-Za-z0-9/]+)', ProjectTemplateFileView.as_view(), name='project_template_download'),
    url(r'^default_info/(?P<parent_commission>\w{2}-\d+)/*$', ProjectDefaultInformationView, name='new_project_defaults')
)
