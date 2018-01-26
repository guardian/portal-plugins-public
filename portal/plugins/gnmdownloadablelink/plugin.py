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


class GnmdownloadablelinkPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "Gnmdownloadablelink App"
        self.urls = 'portal.plugins.gnmdownloadablelink.urls'
        self.urlpattern = r'^gnmdownloadablelink/'
        self.namespace = r'gnmdownloadablelink'
        self.plugin_guid = '3b128671-1b81-4b16-bfa1-2752a5897576'

pluginurls = GnmdownloadablelinkPluginURL()


class GnmdownloadablelinkMasterPagePlugin(Plugin):
    """ Adds the main 'sharing' option to the Master page """
    implements(IPluginBlock)

    def __init__(self):
        self.name = "pluto_guardian_master_extras_right"
        self.plugin_guid = 'a438d05c-f724-4c5a-b2c7-5424cfaebe76'

    def return_string(self, tagname, *args):
        from models import DownloadableLink
        context=args[1]
        master_id = context['master'].id
        return {'guid': self.plugin_guid,
                'template': 'gnmdownloadablelink/share_widget.html',
                'context': {
                    'existing_shares': DownloadableLink.objects.filter(item_id=master_id)
                }
                }

insert = GnmdownloadablelinkMasterPagePlugin()

class GnmdownloadablelinkRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Downloadable Link Registration App"
        self.plugin_guid = '91857312-7183-40e6-989e-f62fe654be25'

    def __call__(self):
        from version import build_number
        _app_dict = {
            'name': 'Downloadable Link Plugin',
            'version': "Build " + str(build_number),
            'author': 'Andy Gallagher <andy.gallagher@theguardian.com>',
            'author_url': '',
            'notes': ''}
        return _app_dict

gnmdownloadablelinkplugin = GnmdownloadablelinkRegister()

class GnmDownloadableLinkCSS(Plugin):
    """
    Injects CSS overrides into all Portal pages; in practise, it will only inject ones with items or collections
    in their context
    """
    implements(IPluginBlock)

    def __init__(self):
        self.name = "header_css_js"
        self.plugin_guid = '46ac18fe-8753-499f-b026-02ca7d9b2e89'
        log.warning('Initiated glacier CSS')

    def return_string(self, tagname, *args):
        """
        Returns a dictionary containing rendering information
        :param tagname: tag name
        :param args: passed in from Portal
        :return: dictionary of context, guid and template
        """
        import traceback
        ctx={}

        return {'guid'    : self.plugin_guid,
                'template': 'gnmdownloadablelink/css_injection_template.html',
                'context' : ctx
                }


cssplug = GnmDownloadableLinkCSS()
