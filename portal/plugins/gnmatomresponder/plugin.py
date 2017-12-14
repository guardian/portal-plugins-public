import logging

from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import (IPluginURL, IPluginBlock, IAppRegister)
from version import build_number

log = logging.getLogger(__name__)


class AtomResponderPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "Atom message responder"
        self.urls = 'portal.plugins.gnmatomresponder.urls'
        self.urlpattern = r'^gnmatomresponder/'
        self.namespace = r'gnmatomresponder'
        self.plugin_guid = 'cd74d14b-89d6-4317-a219-01efc880fc10'


pluginurls = AtomResponderPluginURL()


class AtomResponderRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Atom message Registration App"
        self.plugin_guid = 'd52de962-4009-429c-b126-dc3a957199b1'

    def __call__(self):
        _app_dict = {
            'name': 'Atom Responder plugin',
            'version': "Build " + str(build_number),
            'author': 'Andy Gallagher <andy.gallagher@theguardian.com>',
            'author_url': '',
            'notes': 'Guardian news & media'}
        return _app_dict


register = AtomResponderRegister()