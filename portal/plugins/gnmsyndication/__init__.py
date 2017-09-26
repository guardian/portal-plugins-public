import logging
from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import IPluginURL, IPluginBlock, IAppRegister

log = logging.getLogger(__name__)

class GNMSyndicationRegister(Plugin):
  implements(IAppRegister)

  def __init__(self):
    self.name = "GNM Syndication Dashboard"
    self.plugin_guid = "b0e68714-cf17-11e4-9713-60030890043a"
    log.debug("Registered GNM Syndication Dashboard app")

  def __call__(self):
    _app_dict = {
      'name': self.name,
      'version': "1.0.0",
      'author': 'Andy Gallagher',
      'author_url': 'http://www.theguardian.com/profile/andy-gallagher',
      'notes': 'Statistics and functions for dealing with syndication partners'
    }
    return _app_dict

gnmsyndicationplugin = GNMSyndicationRegister()

class GnmyoutubeAdminPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        self.name = "AdminLeftPanelBottomPanePlugin"
        self.plugin_guid = 'e361d4c5-9683-40e7-81c1-52c0093d5a36'
        log.debug('initiated GNMSyndication admin panel')

    def return_string(self,tagname,*args):
        #raise StandardError("testing")
        return {'guid': self.plugin_guid, 'template': 'gnmsyndication/navigation.html'}

adminplug = GnmyoutubeAdminPlugin()

class GnmSyndicationUrl(Plugin):
    implements(IPluginURL)

    name = 'GNM Syndication URL'
    urls = 'portal.plugins.gnmsyndication.urls'
    urlpattern = r'^gnmsyndication/'
    namespace = 'gnmsyndication'
    plugin_guid = 'e1e3f018-cf17-11e4-861b-60030890043a'


helloworldurlplugin = GnmSyndicationUrl()

