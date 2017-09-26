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

class GnmyoutubePluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "Gnmyoutube App"
        self.urls = 'portal.plugins.gnmyoutube.urls'
        self.urlpattern = r'^gnmyoutube/'
        self.namespace = r'gnmyoutube'
        self.plugin_guid = '5e8deba5-884d-41ea-9e4e-aa4386b3884d'
        log.debug("Initiated Gnmyoutube App")

pluginurls = GnmyoutubePluginURL()


class GnmyoutubeAdminNavigationPlugin(Plugin):
    # This adds your app to the navigation bar
    # Please update the information below with the author etc..
    implements(IPluginBlock)

    def __init__(self):
        self.name = "NavigationAdminPlugin"
        self.plugin_guid = '493a8750-0f41-4237-920f-8b111f03a49c'
        log.debug('Initiated navigation plugin')

    # Returns the template file navigation.html
    # Change navigation.html to the string that you want to use
    def return_string(self, tagname, *args):
        return {'guid': self.plugin_guid, 'template': 'gnmyoutube/navigation.html'}

navplug = GnmyoutubeAdminNavigationPlugin()

class GnmyoutubeAdminPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        self.name = "AdminLeftPanelBottomPanePlugin"
        self.plugin_guid = 'd9ec1946-e446-11e4-8bfb-60030890043a'
        log.debug('initiated GNMYouTube admin panel')

    def return_string(self,tagname,*args):
        #raise StandardError("testing")
        return {'guid': self.plugin_guid, 'template': 'gnmyoutube/navigation.html'}

adminplug = GnmyoutubeAdminPlugin()

class GnmyoutubeRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Gnmyoutube Registration App"
        self.plugin_guid = '7571716e-6b5a-40dc-a783-f44f3b05e889'
        log.debug('Register the App')

    def __call__(self):
        from __init__ import __version__ as versionnumber
        from __init__ import __author__
        _app_dict = {
                'name': 'Gnmyoutube',
                'version': versionnumber,
                'author': __author__,
                'author_url': '',
                'notes': 'By and For GNM Multimedia'}
        return _app_dict

gnmyoutubeplugin = GnmyoutubeRegister()

def make_vidispine_request(agent,method,urlpath,body,headers,content_type='application/xml'):
    import base64
    from django.conf import settings
    import re
    auth = base64.encodestring('%s:%s' % (settings.VIDISPINE_USERNAME, settings.VIDISPINE_PASSWORD)).replace('\n', '')

    headers['Authorization']="Basic %s" % auth
    headers['Content-Type']=content_type
    #conn.request(method,url,body,headers)
    if not re.match(r'^/',urlpath):
        urlpath = '/' + urlpath

    url = "{0}:{1}{2}".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,urlpath)
    logging.debug("URL is %s" % url)
    (headers,content) = agent.request(url,method=method,body=body,headers=headers)
    return (headers,content)
