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

class GnmlibrarytoolPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "Gnmlibrarytool App"
        self.urls = 'portal.plugins.gnmlibrarytool.urls'
        self.urlpattern = r'^gnmlibrarytool/'
        self.namespace = r'gnmlibrarytool'
        self.plugin_guid = 'b430f578-edc5-4508-bd0d-2bd7493d2994'
        log.debug("Initiated Gnmlibrarytool App")

pluginurls = GnmlibrarytoolPluginURL()


class GnmlibrarytoolAdminNavigationPlugin(Plugin):
    # This adds your app to the navigation bar
    # Please update the information below with the author etc..
    implements(IPluginBlock)

    def __init__(self):
        self.name = "NavigationAdminPlugin"
        self.plugin_guid = 'c8202e49-2a15-47a1-9c2e-df396d5485cc'
        log.debug('Initiated navigation plugin')

    # Returns the template file navigation.html
    # Change navigation.html to the string that you want to use
    def return_string(self, tagname, *args):
        return {'guid': self.plugin_guid, 'template': 'gnmlibrarytool/navigation.html'}

navplug = GnmlibrarytoolAdminNavigationPlugin()


class GnmlibrarytoolRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Gnmlibrarytool Registration App"
        self.plugin_guid = 'a2b756a9-1562-4775-94c7-b1309e00ccbc'

    def __call__(self):
        from __init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'Gnmlibrarytool',
                'version': '1.0.0',
                'author': '',
                'author_url': '',
                'notes': '(c) by and for Guardian News and Media'}
        return _app_dict

gnmlibrarytoolplugin = GnmlibrarytoolRegister()

