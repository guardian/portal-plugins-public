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

class GnmSyndicationUrl(Plugin):
    implements(IPluginURL)

    name = 'GNM Syndication URL'
    urls = 'portal.plugins.gnmsyndication.urls'
    urlpattern = r'^gnmsyndication/'
    namespace = 'gnmsyndication'
    plugin_guid = 'e1e3f018-cf17-11e4-861b-60030890043a'

    def __init__(self):
        log.info(GnmSyndicationUrl.name + ' initialized')

helloworldurlplugin = GnmSyndicationUrl()

