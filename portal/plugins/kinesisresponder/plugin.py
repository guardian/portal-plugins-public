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


class GnmkinesisresponderPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "Kinesis responder base plugin"
        self.urls = 'portal.plugins.kinesisresponder.urls'
        self.urlpattern = r'^kinesisresponder/'
        self.namespace = r'kinesisresponder'
        self.plugin_guid = 'c6192389-f763-4ec5-bd1e-5ce050c9f24a'

pluginurls = GnmkinesisresponderPluginURL()


# class GnmkinesisresponderAdminNavigationPlugin(Plugin):
#     # This adds your app to the navigation bar
#     # Please update the information below with the author etc..
#     implements(IPluginBlock)
#
#     def __init__(self):
#         self.name = "NavigationAdminPlugin"
#         self.plugin_guid = 'b418a18f-72f2-4287-bb2e-1942a75826d5'
#         log.debug('Initiated navigation plugin')
#
#     # Returns the template file navigation.html
#     # Change navigation.html to the string that you want to use
#     def return_string(self, tagname, *args):
#         return {'guid': self.plugin_guid, 'template': 'gnmkinesisresponder/navigation.html'}
#
# navplug = GnmkinesisresponderAdminNavigationPlugin()


class GnmkinesisresponderRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Kinesis Responder Registration App"
        self.plugin_guid = 'd52de962-4009-429c-b126-dc3a957199b1'

    def __call__(self):
        from __init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'Kinesis Responder base plugin',
                'version': versionnumber,
                'author': 'Andy Gallagher',
                'author_url': '',
                'notes': '(C) Guardian News & Media'}
        return _app_dict

gnmkinesisresponderplugin = GnmkinesisresponderRegister()

