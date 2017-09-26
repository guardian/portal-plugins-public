import logging
from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import IPluginURL, IPluginBlock, IAppRegister

log = logging.getLogger(__name__)

class LogSearchRegister(Plugin):
  implements(IAppRegister)

  def __init__(self):
    self.name = "GNM Advanced Log Search App"
    self.plugin_guid = "93060d6c-de96-11e4-8b5e-60030890043a"
    log.debug("Registered GNM Advanced Log Search app")

  def __call__(self):
    _app_dict = {
      'name': self.name,
      'version': '1.0.0',
      'author': 'Andy Gallagher',
      'author_url': 'http://www.theguardian.com/profile/andy-gallagher',
      'notes': 'Detailed log search and review'
    }
    return _app_dict

logsearchplugin = LogSearchRegister()

class LogSearchUrl(Plugin):
    implements(IPluginURL)

    name = 'GNM Advanced Log Search URL'
    urls = 'portal.plugins.gnmlogsearch.urls'
    urlpattern = r'^gnmlogsearch/'
    namespace = 'portal.plugins.gnmlogsearch'
    plugin_guid = 'ad0f0f88-de96-11e4-9329-60030890043a'

    def __init__(self):
        log.info(LogSearchUrl.name + ' initialized')

logsearchurlplugin = LogSearchUrl()

