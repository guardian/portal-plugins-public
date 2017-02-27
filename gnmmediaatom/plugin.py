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

class GnmmediaatomPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "Gnmmediaatom App"
        self.urls = 'portal.plugins.gnmmediaatom.urls'
        self.urlpattern = r'^gnmmediaatom/'
        self.namespace = r'gnmmediaatom'
        self.plugin_guid = 'ecb1429e-0709-478e-bd53-45ec49ac9e44'
        log.debug("Initiated Gnmmediaatom App")

pluginurls = GnmmediaatomPluginURL()


class GnmmediaatomAdminNavigationPlugin(Plugin):
    # This adds your app to the navigation bar
    # Please update the information below with the author etc..
    implements(IPluginBlock)

    def __init__(self):
        self.name = "NavigationAdminPlugin"
        self.plugin_guid = '965ceba0-0913-45f0-8481-9db444c17bbd'
        log.debug('Initiated navigation plugin')

    # Returns the template file navigation.html
    # Change navigation.html to the string that you want to use
    def return_string(self, tagname, *args):
        return {'guid': self.plugin_guid, 'template': 'gnmmediaatom/navigation.html'}

navplug = GnmmediaatomAdminNavigationPlugin()


class GnmmediaatomRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Gnmmediaatom Registration App"
        self.plugin_guid = '9c08cc6e-f461-4806-a5d8-0692641d22b5'
        log.debug('Register the App')

    def __call__(self):
        from __init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'Gnmmediaatom',
                'version': '0.0.1',
                'author': '',
                'author_url': '',
                'notes': 'Add your Copyright notice here.'}
        return _app_dict

gnmmediaatomplugin = GnmmediaatomRegister()

