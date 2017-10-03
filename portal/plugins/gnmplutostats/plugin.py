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


class GnmplutostatsPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "Gnmplutostats App"
        self.urls = 'portal.plugins.gnmplutostats.urls'
        self.urlpattern = r'^gnmplutostats/'
        self.namespace = r'gnmplutostats'
        self.plugin_guid = '227c2ab9-e299-4537-99b4-c313a35d1b2e'
        log.debug("Initiated Gnmplutostats App")

pluginurls = GnmplutostatsPluginURL()

class GnmplutostatsAdminPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        self.name = "AdminLeftPanelBottomPanePlugin"
        self.plugin_guid = '46492723-ffda-48d7-8ac9-6951ac5f1bb6'
        log.debug('initiated GNMPlutoStats admin panel')

    def return_string(self,tagname,*args):
        return {'guid': self.plugin_guid, 'template': 'gnmplutostats/navigation.html'}

adminplug = GnmplutostatsAdminPlugin()


class GnmplutostatsAdminNavigationPlugin(Plugin):
    # This adds your app to the navigation bar
    # Please update the information below with the author etc..
    implements(IPluginBlock)

    def __init__(self):
        self.name = "NavigationAdminPlugin"
        self.plugin_guid = '61cae66e-8f49-4a09-bb85-fee609f9d42a'
        log.debug('Initiated navigation plugin')

    # Returns the template file navigation.html
    # Change navigation.html to the string that you want to use
    def return_string(self, tagname, *args):
        return {'guid': self.plugin_guid, 'template': 'gnmplutostats/menu_nav.html'}

navplug = GnmplutostatsAdminNavigationPlugin()


class GnmplutostatsRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Gnmplutostats Registration App"
        self.plugin_guid = 'ff515c21-db4f-4303-af79-aac3577d8ffd'
        log.debug('Register the App')

    def __call__(self):
        from __init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'Gnmplutostats',
                'version': '0.0.1',
                'author': '',
                'author_url': '',
                'notes': 'Add your Copyright notice here.'}
        return _app_dict

gnmplutostatsplugin = GnmplutostatsRegister()

