import logging
from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import IPluginURL, IPluginBlock, IAppRegister

log = logging.getLogger(__name__)

class GNMOptInRegister(Plugin):
    implements(IAppRegister)

    def __init__(self):
        self.name = "GNM Opt In"
        self.plugin_guid = "094B4B3E-E17F-432C-1E21-907E28FE44A7"
        log.debug("Registered GNM Opt In app")

    def __call__(self):
        from version import build_number
        _app_dict = {
            'name': self.name,
            'version': "Build " + str(build_number),
            'author': 'Dave Allison and Andy Gallagher',
            'author_url': 'www.theguardian.com/',
            'notes': 'Allows users to enable certain features.'
        }
        return _app_dict

GNMOptInplugin = GNMOptInRegister()


class GnmOptInUserProfileMenu(Plugin):
    """ Adds a link to the user profile page to manage opt-ins """
    implements(IPluginBlock)

    def __init__(self):
        self.name = "user_settings_menu"
        self.plugin_guid = 'DA17FC48-2E46-479A-ABBC-3AD5902183F3'

    def return_string(self, tagname, *args):
        context=args[1]

        return {'guid': self.plugin_guid,
                'template': 'gnmoptin/user_profile_menu.html',
                'context': {

                }
                }

userProfileMenuPlugin = GnmOptInUserProfileMenu()

class GNMOptInUrl(Plugin):
    implements(IPluginURL)

    name = 'GNM Opt In URL'
    urls = 'portal.plugins.gnmoptin.urls'
    urlpattern = r'^gnmoptin/'
    namespace = 'gnmoptin'
    plugin_guid = 'AC9F2C5E-B78D-4E15-BCF5-91327B0825A8'

    def __init__(self):
        log.info(GNMOptInUrl.name + ' initialized')

GNMOptInurlplugin = GNMOptInUrl()