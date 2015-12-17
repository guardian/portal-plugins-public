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

    #url = "{0}:{1}{2}".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,urlpath)
    url = "http://dc1-mmmw-05.dc1.gnm.int:8080{0}".format(urlpath)
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

class GNMAWSGRRegister(Plugin):
  implements(IAppRegister)

  def __init__(self):
    self.name = "GNM AWS Glacier Restore"
    self.plugin_guid = "26b43a74-ce62-11e4-8e91-002056bc73c6"
    log.debug("Registered GNM AWS Glacier Restore app")

  def __call__(self):
    _app_dict = {
      'name': self.name,
      'version': 0.1,
      'author': 'David Allison',
      'author_url': 'www.theguardian.com/',
      'notes': 'Test'
    }
    return _app_dict

GNMAWSGRplugin = GNMAWSGRRegister()

class GNMAWSGRAdminPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        self.name = "AdminLeftPanelBottomPanePlugin"
        self.plugin_guid = 'e361d4c5-9683-40e7-81c1-12c0093d5a36'
        log.debug('initiated GNMAWSGR admin panel')

    def return_string(self,tagname,*args):
        return {'guid': self.plugin_guid, 'template': 'gnmawsgr/navigation.html'}

GNMAWSGRadminplug = GNMAWSGRAdminPlugin()

class GNMAWSGRUrl(Plugin):
    implements(IPluginURL)

    name = 'GNMAWSGR URL'
    urls = 'portal.plugins.gnmawsgr.urls'
    urlpattern = r'^gnmawsgr/'
    namespace = 'gnmawsgr'
    plugin_guid = '62cdef18-ce63-11e4-aab1-002056bc73c6'

    def __init__(self):
        log.info(GNMAWSGRUrl.name + ' initialized')

GNMAWSGRurlplugin = GNMAWSGRUrl()

class GNMAWSGRGearboxMenuPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        # The name of the plugin which should match the pluginblock tag in the Portal template
        # For instance as defined in media_view.html: {% pluginblock "MediaViewDropdown" %}
        # This plugin is placed in the gearbox menu for the item.
        self.name = "MediaViewDropdown"
        # Define a GUID for each plugin.
        # Use e.g. http://www.guidgenerator.com/
        self.plugin_guid = "02eed808-5c6b-42a7-88a1-0336bcf790d1"
        log.debug("Initiated GNMAWSGRGearboxMenuPlugin")

    def return_string(self, tagname, *args):
        display = 1

        context = args[1]
        item = context['item']
        itemid = item.getId()

        if display == 1:
            return {'guid':self.plugin_guid, 'template':'gearbox_menu.html', 'context' : {'itemid':itemid} }

GNMAWSGRpluginblock = GNMAWSGRGearboxMenuPlugin()

class GNMAWSGRCollectionGearboxMenuPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        # The name of the plugin which should match the pluginblock tag in the Portal template
        # For instance as defined in media_view.html: {% pluginblock "MediaViewDropdown" %}
        # This plugin is placed in the gearbox menu for the item.
        self.name = "CollectionViewDropdown"
        # Define a GUID for each plugin.
        # Use e.g. http://www.guidgenerator.com/
        self.plugin_guid = "05eed808-5c6b-42a7-88a1-0336bcf790d1"
        log.debug("Initiated GNMAWSGRCollectionGearboxMenuPlugin")

    def return_string(self, tagname, *args):
        display = 1
        if display == 1:
            return {'guid':self.plugin_guid, 'template':'collection_gearbox_menu.html'}

GNMAWSGRCollectionpluginblock = GNMAWSGRCollectionGearboxMenuPlugin()

class GNMAWSGRBinGearboxMenuPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        # The name of the plugin which should match the pluginblock tag in the Portal template
        # For instance as defined in media_view.html: {% pluginblock "MediaViewDropdown" %}
        # This plugin is placed in the gearbox menu for the item.
        self.name = "MediaBinDropdown"
        # Define a GUID for each plugin.
        # Use e.g. http://www.guidgenerator.com/
        self.plugin_guid = "07eed808-5c6b-42a7-88a1-0336bcf790d1"
        log.debug("Initiated GNMAWSGRBinGearboxMenuPlugin")

    def return_string(self, tagname, *args):
        display = 1
        if display == 1:
            return {'guid':self.plugin_guid, 'template':'bin_gearbox_menu.html'}

GNMAWSGRBinpluginblock = GNMAWSGRBinGearboxMenuPlugin()