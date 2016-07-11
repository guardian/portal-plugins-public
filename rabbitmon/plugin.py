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

class RabbitmonPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "Rabbitmon App"
        self.urls = 'portal.plugins.rabbitmon.urls'
        self.urlpattern = r'^rabbitmon/'
        self.namespace = r'rabbitmon'
        self.plugin_guid = 'e73cbb2d-a9e8-4892-8bff-14be0f174f6b'
        log.debug("Initiated Rabbitmon App")

pluginurls = RabbitmonPluginURL()


class RabbitmonAdminNavigationPlugin(Plugin):
    # This adds your app to the navigation bar
    # Please update the information below with the author etc..
    implements(IPluginBlock)

    def __init__(self):
        self.name = "NavigationAdminPlugin"
        self.plugin_guid = 'f7454f89-37df-4c4e-87a2-1320a24a69a0'
        log.debug('Initiated navigation plugin')

    # Returns the template file navigation.html
    # Change navigation.html to the string that you want to use
    def return_string(self, tagname, *args):
        return {'guid': self.plugin_guid, 'template': 'rabbitmon/navigation.html'}

navplug = RabbitmonAdminNavigationPlugin()


class RabbitmonRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Rabbitmon Registration App"
        self.plugin_guid = '975ba878-a343-4599-9b3f-582e648be303'
        log.debug('Register the App')

    def __call__(self):
        from __init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'Rabbitmon',
                'version': '0.0.1',
                'author': '',
                'author_url': '',
                'notes': 'Add your Copyright notice here.'}
        return _app_dict

rabbitmonplugin = RabbitmonRegister()

