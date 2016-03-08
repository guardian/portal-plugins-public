"""

"""
import logging

from django.conf.urls.defaults import *
from views import ProjectTemplateFileView,ProjectDefaultInformationView,ProjectListView,CommissionListView,\
    WorkingGroupListView, CommissionerListView, ProjectTypeListView,ProjectSubTypeListView,ProjectMakeView,\
    AssetFolderCreatorView, InstallationCheckView
# This new app handles the request to the URL by responding with the view which is loaded 
# from portal.plugins.gnmextprojecthelper.views.py. Inside that file is a class which responsedxs to the 
# request, and sends in the arguments template - the html file to view.
# name is shortcut name for the urls.

urlpatterns = patterns('portal.plugins.gnmextprojecthelper.views',
    url(r'^$', 'GenericAppView', kwargs={'template': 'gnmextprojecthelper/index.html'}, name='index'),
    url(r'^get_template/(?P<project_type>.+)$', ProjectTemplateFileView.as_view(), name='project_template_download'),
    url(r'^default_info/(?P<parent_commission>\w{2}-\d+)/*$', ProjectDefaultInformationView, name='new_project_defaults'),
    url(r'^project_list/(?P<commission_id>\w{2}-\d+)/*$', ProjectListView.as_view(), name='projects_for_commission'),
    url(r'^commission_list/(?P<working_group>[\w\d]{8}-[\w\d]{4}-[\w\d]{4}-[\w\d]{4}-[\w\d]+)/*$',CommissionListView.as_view(), name='commissions_for_group'),
    url(r'^working_group_list/*$', WorkingGroupListView.as_view(), name='working_groups'),
    url(r'^commissioner_list/*$', CommissionerListView.as_view(), name='commissioners'),
    url(r'^project_type_list/*$', ProjectTypeListView.as_view(), name='project_types'),
    url(r'^project_subtype_list/(?P<project_type>[\w\d]+)/*$', ProjectSubTypeListView.as_view(), name='project_types'),
    url(r'^new_project/\w{2}-\d+/assetfolder', AssetFolderCreatorView.as_view(), name="asset_folder"),
    url(r'^new_project/(?P<commission_id>\w{2}-\d+)/*$', ProjectMakeView.as_view(), name='make_project'),
    url(r'^is_installed$', InstallationCheckView.as_view(), name="installation_check")
)
