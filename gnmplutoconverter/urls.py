"""

"""
import logging

from django.conf.urls.defaults import *
from views import WorkingGroupListView, CommissionListView, ProjectListView
# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.gnmplutoconverter.views.py. Inside that file is a class which responsedxs to the 
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.gnmplutoconverter.views',
    url(r'^$', 'GenericAppView', kwargs={'template': 'gnmplutoconverter/index.html'}, name='index'),
    url(r'^workinggroups$', WorkingGroupListView.as_view(), name="working_groups" ),
    url(r'^commissions$', CommissionListView.as_view(), name="commission_list"),
    url(r'^projects$', ProjectListView.as_view(), name="project_list"),
)
