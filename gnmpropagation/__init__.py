import logging
from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import IPluginURL, IPluginBlock, IAppRegister

log = logging.getLogger(__name__)

def make_vidispine_request(agent,method,urlpath,body,headers,content_type='application/xml'):
    import base64
    from django.conf import settings
    import re
    auth = base64.encodestring('%s:%s' % (settings.VIDISPINE_USERNAME, settings.VIDISPINE_PASSWORD)).replace('\n', '')

    headers['Authorization']="Basic %s" % auth
    headers['Content-Type']=content_type

    if not re.match(r'^/',urlpath):
        urlpath = '/' + urlpath

    url = "{0}:{1}{2}".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,urlpath)
    #url = "http://dc1-mmmw-05.dc1.gnm.int:8080{0}".format(urlpath)
    logging.debug("URL is %s" % url)
    (headers,content) = agent.request(url,method=method,body=body,headers=headers)
    return (headers,content)

def getItemInfo(itemid,agent=None):
    import json
    if agent is None:
        import httplib2
        agent = httplib2.Http()

    url = "/API/item/{0}".format(itemid)

    (headers,content) = make_vidispine_request(agent,"GET",url,body="",headers={'Accept': 'application/json'})
    if int(headers['status']) < 200 or int(headers['status']) > 299:
        #logging.error(content)
        #raise StandardError("Vidispine error: %s" % headers['status'])
        return None

    return json.loads(content)

def getBinInfo(agent=None):
    import json
    if agent is None:
        import httplib2
        agent = httplib2.Http()

    url = "/API/v1/mediabin/"

    (headers,content) = make_vidispine_request(agent,"GET",url,body="",headers={'Accept': 'application/json'})
    if int(headers['status']) < 200 or int(headers['status']) > 299:
        #logging.error(content)
        #raise StandardError("Vidispine error: %s" % headers['status'])
        return None

    return json.loads(content)

class GNMPropagationRegister(Plugin):
  implements(IAppRegister)

  def __init__(self):
    self.name = "GNM Propagation"
    self.plugin_guid = "094B4B3E-E17E-434C-9E21-907E27FE44A7"
    log.debug("Registered GNM Propagation app")

  def __call__(self):
    _app_dict = {
      'name': self.name,
      'version': "0.0.1",
      'author': 'Dave Allison and Andy Gallagher',
      'author_url': 'www.theguardian.com/',
      'notes': 'Propagates meta data fields.'
    }
    return _app_dict

GNMPropagationplugin = GNMPropagationRegister()

class GNMPropagationUrl(Plugin):
    implements(IPluginURL)

    name = 'GNM Propagation URL'
    urls = 'portal.plugins.gnmpropagation.urls'
    urlpattern = r'^gnmpropagation/'
    namespace = 'gnmpropagation'
    plugin_guid = 'AB9F2C5E-B68D-4E17-BCF5-96327B0825A8'

    def __init__(self):
        log.info(GNMPropagationUrl.name + ' initialized')

GNMPropagationurlplugin = GNMPropagationUrl()
