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


class GnmplutoconverterPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "Gnmplutoconverter App"
        self.urls = 'portal.plugins.portal.plugins.gnmplutoconverter.urls'
        self.urlpattern = r'^portal.plugins.gnmplutoconverter/'
        self.namespace = r'portal.plugins.gnmplutoconverter'
        self.plugin_guid = '09346faa-6818-4ec3-88aa-8a7c8dde054e'
        log.debug("Initiated Gnmplutoconverter App")

pluginurls = GnmplutoconverterPluginURL()


class GnmplutoconverterRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Gnmplutoconverter Registration App"
        self.plugin_guid = '38d7f1ff-2a5c-441a-9614-7864be3e457e'
        log.debug('Register the App')

    def __call__(self):
        from __init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'Pluto Converter App',
                'version': versionnumber,
                'author': 'Andy Gallagher',
                'author_url': '',
                'notes': 'Add your Copyright notice here.'}
        return _app_dict

gnmplutoconverterplugin = GnmplutoconverterRegister()


class PlutoConverterGenericGearboxPlugin(Plugin):
    implements(IPluginBlock)

    def return_string(self, tagname, context, request_context):
        from traceback import format_exc
        ctx={}

        try:
            i = request_context['item']
            ctx['itemid'] = i.getId()
            ctx['gnm_type'] = i.getMetadataFieldValueByName('gnm_type')
            ctx['mediaType'] = i.getMetadataFieldValueByName('mediaType')
        except Exception as e:
            print u"{0}: {1}".format(e.__class__.__name__,e.message)
            print format_exc()

        print "PlutoConverterGearboxPlugin: tagname {0}".format(tagname)
        return {
            'guid': self.plugin_guid,
            'template': 'portal.plugins.gnmplutoconverter/navigation.html',
            'context': ctx,
            #'string': 'PlutoConverterGearbox',
        }


class PlutoConverterGearboxPlugin(PlutoConverterGenericGearboxPlugin):
    def __init__(self):
        self.name = "MediaViewDropdown" #MediaViewDropdown => "gearbox" menu on item page, and on item pod view.
        # SearchViewDropdown => ???
        self.plugin_guid = '78f4afe1-9367-44da-818d-f0d75c718ba4'
        log.debug("Registering PlutoConverterGearboxPlugin")

gnmplutoconvertergearbo = PlutoConverterGearboxPlugin()
