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

class GnmnewshoundPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "Gnmnewshound App"
        self.urls = 'portal.plugins.gnmnewshound.urls'
        self.urlpattern = r'^gnmnewshound/'
        self.namespace = r'gnmnewshound'
        self.plugin_guid = 'a86a6533-aa70-43f3-85fe-8aae6ac0dd85'
        log.debug("Initiated Gnmnewshound App")

pluginurls = GnmnewshoundPluginURL()


class GnmnewshoundAdminNavigationPlugin(Plugin):
    # This adds your app to the navigation bar
    # Please update the information below with the author etc..
    implements(IPluginBlock)

    def __init__(self):
        self.name = "NavigationAdminPlugin"
        self.plugin_guid = '344204f0-117b-4ccd-9aff-941a111ad780'
        log.debug('Initiated navigation plugin')

    # Returns the template file navigation.html
    # Change navigation.html to the string that you want to use
    def return_string(self, tagname, *args):
        return {'guid': self.plugin_guid, 'template': 'gnmnewshound/navigation.html'}

navplug = GnmnewshoundAdminNavigationPlugin()


class GnmnewshoundRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Gnmnewshound Registration App"
        self.plugin_guid = '505144cd-e3f8-4652-8259-2dd5f13eef97'
        log.debug('Register the App')

    def __call__(self):
        from __init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'Gnmnewshound',
                'version': '0.0.1',
                'author': '',
                'author_url': '',
                'notes': 'Add your Copyright notice here.'}
        return _app_dict

gnmnewshoundplugin = GnmnewshoundRegister()

