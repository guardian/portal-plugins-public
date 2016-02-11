"""
This is your new plugin handler code.

Put your plugin handling code in here. remember to update the __init__.py file with 
you app version number. We have automatically generated a GUID for you, namespace, and a url 
that serves up index.html file
"""
import logging

from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import (IPluginURL, IPluginBlock, IAppRegister)

log = logging.getLogger(__name__)

class GnmextprojecthelperPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "GNM External Projects Helper App"
        self.urls = 'portal.plugins.gnmextprojecthelper.urls'
        self.urlpattern = r'^gnmextprojecthelper/'
        self.namespace = r'gnmextprojecthelper'
        self.plugin_guid = '98085ae9-c5bc-400e-a526-5ea9902f6f9c'
        log.debug("Initiated Gnmextprojecthelper App")

pluginurls = GnmextprojecthelperPluginURL()

#
# class GnmextprojecthelperAdminNavigationPlugin(Plugin):
#     # This adds your app to the navigation bar
#     # Please update the information below with the author etc..
#     implements(IPluginBlock)
#
#     def __init__(self):
#         self.name = "NavigationAdminPlugin"
#         self.plugin_guid = '58af3b6e-c8fe-4704-a9bc-be7644f14db7'
#         log.debug('Initiated navigation plugin')
#
#     # Returns the template file navigation.html
#     # Change navigation.html to the string that you want to use
#     def return_string(self, tagname, *args):
#         return {'guid': self.plugin_guid, 'template': 'gnmextprojecthelper/navigation.html'}
#
# navplug = GnmextprojecthelperAdminNavigationPlugin()


class GnmextprojecthelperRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "GNM External Projects Helper App"
        self.plugin_guid = '3e5313b2-9705-4faf-9d57-d098a97b7293'

    def __call__(self):
        from __init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'GNM External Projects Helper App',
                'version': '0.0.1',
                'author': 'Andy Gallagher',
                'author_url': '',
                'notes': '(C) GNM'}
        return _app_dict

gnmextprojecthelperplugin = GnmextprojecthelperRegister()

