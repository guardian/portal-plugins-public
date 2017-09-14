"""
This is your new plugin handler code.

Put your plugin handling code in here. remember to update the __init__.py file with 
you app version number. We have automatically generated a GUID for you, namespace, and a url 
that serves up index.html file
"""
import logging

from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import (IPluginURL, IPluginBlock, IAppRegister,)

log = logging.getLogger(__name__)


class GnmgridintegrationPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "Gnmgridintegration App"
        self.urls = 'portal.plugins.portal.plugins.gnmgridintegration.urls'
        self.urlpattern = r'^portal.plugins.gnmgridintegration/'
        self.namespace = r'portal.plugins.gnmgridintegration'
        self.plugin_guid = '435bd5e0-17e5-41db-9cd9-8e26917a0dc2'
        log.debug("Initiated Gnmgridintegration App")

pluginurls = GnmgridintegrationPluginURL()


class GnmgridintegrationAdminNavigationPlugin(Plugin):
    # This adds your app to the navigation bar
    # Please update the information below with the author etc..
    implements(IPluginBlock)

    def __init__(self):
        self.name = "NavigationAdminPlugin"
        self.plugin_guid = 'a592ba44-f8b0-41b5-af7d-eda70e0e76ca'
        log.debug('Initiated navigation plugin')

    # Returns the template file navigation.html
    # Change navigation.html to the string that you want to use
    def return_string(self, tagname, *args):
        return {'guid': self.plugin_guid, 'template': 'portal.plugins.gnmgridintegration/menu_nav.html'}

navplug = GnmgridintegrationAdminNavigationPlugin()


# class GnmgridintegrationItemPanelPlugin(Plugin):
#     """
#     Plugin for the item view menu item.  This works with two other panel plugins to show the item page panel.
# See p. 202 of Portal Plugin Developers Guide
#     """
#     implements(IPluginBlock)
#
#     def __init__(self):
#         self.name = "MediaViewLeftPanelMenu"
#         self.plugin_guid = '5d022c84-7f33-4ce7-919f-c153494a1443'
#
#     def return_string(self, tagname, *args):
#         return {'guid': self.plugin_guid, 'string': '<li>Grid Images</li>'}
#
# pbnewmenuitem = GnmgridintegrationItemPanelPlugin()

class GnmgridintegrationRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Gnmgridintegration Registration App"
        self.plugin_guid = '88bac770-61c2-4062-8e47-7da2f4275792'
        log.debug('Register the App')

    def __call__(self):
        from __init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'Gnmgridintegration',
                'version': '0.0.1',
                'author': '',
                'author_url': '',
                'notes': 'Add your Copyright notice here.'}
        return _app_dict

gnmgridintegrationplugin = GnmgridintegrationRegister()

class GnmgridintegrationAdminPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        self.name = "AdminLeftPanelBottomPanePlugin"
        self.plugin_guid = '285f1224-de4a-11e5-99ff-60030890043a'
        log.debug('initiated GNMPurgeMeister admin panel')

    def return_string(self,tagname,*args):
        #raise StandardError("testing")
        return {'guid': self.plugin_guid, 'template': 'portal.plugins.gnmgridintegration/navigation.html'}

adminplug = GnmgridintegrationAdminPlugin()
