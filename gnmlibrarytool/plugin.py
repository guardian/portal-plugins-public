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


class GnmlibrarytoolItemViewPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        #print "init library tool item view"
        self.name = "MediaViewLeftPanelMenu"
        self.plugin_guid = '5101c687-aa07-4238-a4e9-c5b6f37aade6'

    def return_string(self,tagname,*args):
        context = args[1]
        item = context['item']
        iid = item.getId()
        return {'guid': self.plugin_guid, 'template': 'gnmlibrarytool/mediaviewmenuitem.html', 'context': {'item_id': iid}}

gnmlibrarytoolitemviewplugin = GnmlibrarytoolItemViewPlugin()


class GnmlibrarytoolSRViewJS(Plugin):
    implements(IPluginBlock)

    jsstring = """
        <script src="/sitemedia/gnmlibrarytool/js/storagerulepanel.js"></script>
        <script type="text/javascript" charset="utf-8">
        $(document).ready(function() {
            // Extend the namespace with a new viewclass.
            (function (app, $, undefined) {
                app.MediaItemMoreInfoPanel = cntmo.prtl.ViewClass.extend();
            }( cntmo.app = cntmo.app || {}, jQuery ));

            // Create a new instance of the viewclass that can
            // be switched to.
            cntmo.prtl.panelviews['GnmLibraryToolSRPanel'] = new cntmo.app.MediaItemMoreInfoPanel({el:$('#GnmLibraryToolSRPanel')});
        });
        </script>
    """

    def __init__(self):
        #print "init inlinejs"
        self.name = "MediaViewInLineJS"
        self.plugin_guid = '7e35bced-330f-456c-b472-e8263ad4236a'

    def return_string(self, tagname,*args):
        return {'guid': self.plugin_guid, 'string': self.jsstring }

gnmlibtooljsplugin = GnmlibrarytoolSRViewJS()


class GnmlibrarytoolStorageRulesViewPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        self.name = "MediaViewPanelRow2"
        self.plugin_guid = "2b849f0f-0509-4edb-98a0-78da05e60682"

    def return_string(self,tagname,*args):
        from models import LibraryStorageRule
        rules = LibraryStorageRule.objects.all()
        rules = sorted(rules.values("storagerule_name"))
        context = args[1]
        item = context['item']
        iid = item.getId()
        return {'guid': self.plugin_guid, 'template': 'gnmlibrarytool/mediaview_storagerules.html', 'context': {'rules': rules, 'item_id': iid}}

gnmlibrarytoolSRviewplugin = GnmlibrarytoolStorageRulesViewPlugin()