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


class RavenjsInject(Plugin):
    """
    Injects Raven into the javascript block of each Portal page
    """
    implements(IPluginBlock)

    def __init__(self):
        self.name = "BaseJS"
        self.plugin_guid = '46ac18fe-8753-499f-b026-02ca7d9b2e89'
        log.warning('Initiated RavenjsInject')

    def return_string(self, tagname, *args):
        """
        Returns a dictionary containing rendering information
        :param tagname: tag name
        :param args: passed in from Portal
        :return: dictionary of context, guid and template
        """
        import traceback
        from django.conf import settings
        log.debug("loading RavenjsInject")
        try:
            raven_dsn = settings.RAVEN_CONFIG
            if not "public_dsn" in raven_dsn:
                log.error("Raven not configured properly.  RAVEN_CONFIG found but it's either not a dictionary or does not contain the 'public_dsn' key.")
                return None

            return {'guid'    : self.plugin_guid,
                    'template': 'ravenjs/raven_injection_template.html',
                    'context' : {'raven_dsn': raven_dsn['public_dsn']}
                    }
        except AttributeError:
            log.error("Raven does not appear to be installed correctly. Unable to get the RAVEN_CONFIG setting. Check your settings files.")
            return None
        except Exception:
            log.error(traceback.print_exc())
            return None

injectplugin = RavenjsInject()

class RavenjsRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "Ravenjs Registration App"
        self.plugin_guid = '6e212936-7897-442b-8bb1-345f1e55bcea'

    def __call__(self):
        from __init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'RavenJS',
                'version': '1.0.0',
                'author': 'Andy Gallagher <andy.gallagher@theguardian.com>',
                'author_url': '',
                'notes': 'Adds Sentry integration to Portal\'s javascript'}
        return _app_dict

ravenjsplugin = RavenjsRegister()

