import logging
from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import IPluginURL, IPluginBlock, IAppRegister

log = logging.getLogger(__name__)

class HelloWorldRegister(Plugin):
  implements(IAppRegister)

  def __init__(self):
    self.name = "Hello World App"
    self.plugin_guid = "26b43a74-ce62-11e4-8e91-005056bc73c6"
    log.debug("Registered Hello World app")

  def __call__(self):
    _app_dict = {
      'name': self.name,
      'version': 1,
      'author': 'Andy Gallagher',
      'author_url': 'http://www.theguardian.com/profile/andy-gallagher',
      'notes': 'First simple test'
    }
    return _app_dict

helloworldplugin = HelloWorldRegister()

class HelloWorldUrl(Plugin):
    implements(IPluginURL)

    name = 'Hello World URL'
    urls = 'portal.plugins.helloworld.urls'
    urlpattern = r'^ag_helloworld/'
    namespace = 'portal.plugins.helloworld'
    plugin_guid = '62cdef18-ce63-11e4-aab1-005056bc73c6'

    def __init__(self):
        log.info(HelloWorldUrl.name + ' initialized')

helloworldurlplugin = HelloWorldUrl()

