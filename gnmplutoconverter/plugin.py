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
        self.urls = 'portal.plugins.gnmplutoconverter.urls'
        self.urlpattern = r'^gnmplutoconverter/'
        self.namespace = r'gnmplutoconverter'
        self.plugin_guid = '09346faa-6818-4ec3-88aa-8a7c8dde054e'
        log.debug("Initiated Gnmplutoconverter App")

pluginurls = GnmplutoconverterPluginURL()


# class GnmplutoconverterAdminNavigationPlugin(Plugin):
#     # This adds your app to the navigation bar
#     # Please update the information below with the author etc..
#     implements(IPluginBlock)
#
#     def __init__(self):
#         self.name = "NavigationAdminPlugin"
#         self.plugin_guid = '682ba2bd-24e0-41d8-ae85-fc711a51e505'
#         log.debug('Initiated navigation plugin')
#
#     # Returns the template file navigation.html
#     # Change navigation.html to the string that you want to use
#     def return_string(self, tagname, *args):
#         return {'guid': self.plugin_guid, 'template': 'gnmplutoconverter/navigation.html'}
#
# navplug = GnmplutoconverterAdminNavigationPlugin()


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
        #from portal.vidispine.iitem import ItemHelper
        from pprint import pprint
        from traceback import format_exc
        ctx={}
        #pprint(current_context)

        #print "Got {0} args".format(len(args))
        try:
            # #args[1] is a RequestContext object
            # for d in request_context.dicts:
            #     pprint(d)
            #     print "-------------------------------\n"
            # for k,v in request_context.__dict__.items():
            #     if k=='dicts': continue
            #     print "{0} => {1}".format(k,v)
            #     print "-------------------------------\n"
            i = request_context['item']
            #iid = request_context['itemid']
            #pprint(i.__dict__)
            #help(i)
            #print "Item ID is {0}".format(i.getId())
            #pprint(i.getMetadataFieldValueByName('title'))
            ctx['itemid'] = i.getId()
            ctx['gnm_type'] = i.getMetadataFieldValueByName('gnm_type')
            ctx['mediaType'] = i.getMetadataFieldValueByName('mediaType')
        except Exception as e:
            type = ""
            print u"{0}: {1}".format(e.__class__.__name__,e.message)
            print format_exc()



        #pprint(args)
        #pprint(kwargs)
        #item = current_context['item']
        #itemid = item.getId()
        #pprint(item)

        #ith = ItemHelper()

        #res = ith.getItemMetadata(itemid)

        print "PlutoConverterGearboxPlugin: tagname {0}".format(tagname)
        return {
            'guid': self.plugin_guid,
            'template': 'gnmplutoconverter/navigation.html',
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
