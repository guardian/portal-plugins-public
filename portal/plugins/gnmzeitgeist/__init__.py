import logging
from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import IPluginURL, IPluginBlock, IAppRegister

log = logging.getLogger(__name__)

class GnmZeitgeistRegister(Plugin):
  implements(IAppRegister)

  def __init__(self):
    self.name = "GNM Tag Clouds App"
    self.plugin_guid = "b0e9a1c2-d180-11e4-8a3b-60030890043a"
    log.debug("Registered GnmZeitgeist app")

  def __call__(self):
    _app_dict = {
      'name': self.name,
      'version': "1.0.0",
      'author': 'Andy Gallagher',
      'author_url': 'http://www.theguardian.com/profile/andy-gallagher',
      'notes': 'Shows tag clouds of what is being uploaded at the moment'
    }
    return _app_dict

helloworldplugin = GnmZeitgeistRegister()

class GnmZeitgeistUrl(Plugin):
    implements(IPluginURL)

    name = 'GNM tag cloud app URL'
    urls = 'portal.plugins.gnmzeitgeist.urls'
    urlpattern = r'^gnmtagcloud/'
    namespace = 'portal.plugins.gnmzeitgeist'
    plugin_guid = 'b598f7ae-d180-11e4-beea-60030890043a'

    def __init__(self):
        log.info(GnmZeitgeistUrl.name + ' initialized')

helloworldurlplugin = GnmZeitgeistUrl()

