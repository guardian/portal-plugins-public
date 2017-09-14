import logging
from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import IPluginURL, IPluginBlock, IAppRegister

log = logging.getLogger(__name__)

class GNMPropagationRegister(Plugin):
  implements(IAppRegister)

  def __init__(self):
    self.name = "GNM Propagation"
    self.plugin_guid = "094B4B3E-E17E-434C-9E21-907E27FE44A7"
    log.debug("Registered GNM Propagation app")

  def __call__(self):
    _app_dict = {
      'name': self.name,
      'version': "1.0",
      'author': 'Dave Allison and Andy Gallagher',
      'author_url': 'www.theguardian.com/',
      'notes': 'Propagates meta data fields.'
    }
    return _app_dict

GNMPropagationplugin = GNMPropagationRegister()

class GNMPropagationUrl(Plugin):
    implements(IPluginURL)

    name = 'GNM Propagation URL'
    urls = 'portal.plugins.portal.plugins.gnmpropagation.urls'
    urlpattern = r'^portal.plugins.gnmpropagation/'
    namespace = 'portal.plugins.gnmpropagation'
    plugin_guid = 'AB9F2C5E-B68D-4E17-BCF5-96327B0825A8'

    def __init__(self):
        log.info(GNMPropagationUrl.name + ' initialized')

GNMPropagationurlplugin = GNMPropagationUrl()
