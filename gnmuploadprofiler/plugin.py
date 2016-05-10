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

class GnmuploadprofilerPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "GNM Upload Profiler"
        self.urls = 'portal.plugins.gnmuploadprofiler.urls'
        self.urlpattern = r'^gnmuploadprofiler/'
        self.namespace = r'gnmuploadprofiler'
        self.plugin_guid = '100fb673-fc07-4f18-9e9c-f85717238936'
        log.debug("Initiated Gnmuploadprofiler App")

pluginurls = GnmuploadprofilerPluginURL()


class GnmuploadprofilerAdminNavigationPlugin(Plugin):
    # This adds your app to the navigation bar
    # Please update the information below with the author etc..
    implements(IPluginBlock)

    def __init__(self):
        self.name = "NavigationAdminPlugin"
        self.plugin_guid = '9ae6bea9-4150-4c52-aa43-645ca2f03132'
        log.debug('Initiated navigation plugin')

    # Returns the template file navigation.html
    # Change navigation.html to the string that you want to use
    def return_string(self, tagname, *args):
        return {'guid': self.plugin_guid, 'template': 'gnmuploadprofiler/navigation.html'}

navplug = GnmuploadprofilerAdminNavigationPlugin()


class GnmuploadprofilerRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Gnmuploadprofiler Registration App"
        self.plugin_guid = '99dc7aa3-2e10-4f16-84fe-8fecc32e4668'
        log.debug('Register the App')

    def __call__(self):
        from __init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'Upload Speed Profiler',
                'version': versionnumber,
                'author': 'Andy Gallagher <andy.gallagher@theguardian.com>',
                'author_url': '',
                'notes': 'GNM internal software'}
        return _app_dict

gnmuploadprofilerplugin = GnmuploadprofilerRegister()

