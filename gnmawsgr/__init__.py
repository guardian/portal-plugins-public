import logging
from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import IPluginURL, IPluginBlock, IAppRegister

archive_test_value = 'Archived'
restoring_test_value = 'Requested Restore'
archiving_test_value = 'Requested Archive'

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
    logging.debug("URL is %s" % url)
    (headers,content) = agent.request(url,method=method,body=body,headers=headers)
    return (headers,content)


class Gnm_ProjectRestoreOption(Plugin):
    """
    Injects an option to restore a project into the project view
    """
    implements(IPluginBlock)

    def __init__(self):
        self.name = "pluto_project_edit_extras_right"
        self.plugin_guid = '4506fd78-6e1b-4e5e-a6a0-674ae0ca5c41'
        log.debug('Initiated project page plugin')

    def return_string(self, tagname, *args):
        """
        Renders a template of html to inject into the project page, containing an opening link and controls that call
        our AJAX views
        :param tagname:
        :param args:
        :return:
        """
        context = args[1]
        project = context['project']
        projectmodel = context['projectmodel']
        project_id = project.id

        print context['user'].groups.all()
        
        is_allowed = False
        if context['user'].is_superuser:
            is_allowed = True
        else:
            list = filter(lambda group: True if group.name=='AWS_GR_Restore' else False,context['user'].groups.all())
            if len(list)>0: is_allowed=True
            
        print is_allowed
        
        return {'guid': self.plugin_guid,
                'template': 'gnmawsgr/project_restore_request.html',
                'context': {
                    'collection': project_id,
                    'is_allowed': is_allowed
                }}

navplug = Gnm_ProjectRestoreOption()


class Gnm_GlacierCSS(Plugin):
    """
    Injects CSS overrides into all Portal pages; in practise, it will only inject ones with items or collections
    in their context
    """
    implements(IPluginBlock)
    
    def __init__(self):
        self.name = "header_css_js"
        self.plugin_guid = '46ac18fe-8753-499f-b026-02ca7d9b2e89'
        log.warning('Initiated glacier CSS')
    
    def context_for_item(self, item):
        """
        Return a simplified context dictionary of item attributes that we're interested in
        :param item: item ref
        :return: dictionary
        """
        from pprint import pprint
        from utils import metadataValueInGroup, item_is_archived, item_is_restoring, item_will_be_archived
        
        print item.__class__.__name__
        print dir(item)
        pprint(item.item_metadata)

        return {
            'object_class': 'item',
            'is_archiving': item_will_be_archived(item.item_metadata),
            'is_restoring': item_is_restoring(item.item_metadata),
            'is_archived': item_is_archived(item.item_metadata),
        }
    
    
    def context_for_collection(self, collection):
        return {}
    
    def return_string(self, tagname, *args):
        """
        Returns a dictionary containing rendering information
        :param tagname: tag name
        :param args: passed in from Portal
        :return: dictionary of context, guid and template
        """
        import traceback
        try:
            context = args[1]
            if 'item' in context:
                ctx=self.context_for_item(context['item'])
            elif 'collection' in context:
                ctx=self.context_for_collection(context['collection'])
            else:
                print "no item or collection in context"
                ctx={}
        except Exception:
            traceback.print_exc()
            ctx = {}
            
        return {'guid': self.plugin_guid,
                'template': 'gnmawsgr/css_injection_template.html',
                'context': ctx
                }
    
cssplug = Gnm_GlacierCSS()


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

class GNMAWSGRRegister(Plugin):
  implements(IAppRegister)

  def __init__(self):
    self.name = "GNM AWS Glacier Restore"
    self.plugin_guid = "7ACD5601-1255-4E70-8DC7-AB88188F06AF"
    log.debug("Registered GNM AWS Glacier Restore app")

  def __call__(self):
    _app_dict = {
      'name': self.name,
      'version': "1.0.0",
      'author': 'Dave Allison and Andy Gallagher',
      'author_url': 'www.theguardian.com/',
      'notes': 'Allows restoration of items and collections from the Amazon Web Services Glacier system.'
    }
    return _app_dict

GNMAWSGRplugin = GNMAWSGRRegister()

class GNMAWSGRAdminPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        self.name = "AdminLeftPanelBottomPanePlugin"
        self.plugin_guid = '3E43F026-1DB4-446B-B3A2-3A953597D7B2'
        log.debug('initiated GNMAWSGR admin panel')

    def return_string(self,tagname,*args):
        return {'guid': self.plugin_guid, 'template': 'gnmawsgr/navigation.html'}


GNMAWSGRadminplug = GNMAWSGRAdminPlugin()

class GNMAWSGRAdminNavigationPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        self.name = "NavigationAdminPlugin"
        self.plugin_guid = 'FC1732F9-A02E-4355-8BA0-F67924DECA5F'
        log.debug('Initiated navigation plugin')

    def return_string(self, tagname, *args):
        return {'guid': self.plugin_guid, 'template': 'gnmawsgr/menu.html'}

GNMAWSGRnavplug = GNMAWSGRAdminNavigationPlugin()

class GNMAWSGRUrl(Plugin):
    implements(IPluginURL)

    name = 'GNMAWSGR URL'
    urls = 'portal.plugins.gnmawsgr.urls'
    urlpattern = r'^gnmawsgr/'
    namespace = 'gnmawsgr'
    plugin_guid = 'A68B511D-078A-46DD-BE8D-5A4F2290ADC8'

    def __init__(self):
        log.info(GNMAWSGRUrl.name + ' initialized')

GNMAWSGRurlplugin = GNMAWSGRUrl()


class GNMAWSGRGearboxMenuPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        self.name = "MediaViewDropdown"
        self.plugin_guid = "1C0AC202-FB08-4BB0-8296-871385A7BC6B"
        log.debug("Initiated GNMAWSGRGearboxMenuPlugin")

    def recurse_for_field(self, mdkey, data):
        for f in data:
            if f['name'] == mdkey:
                return map(lambda x: x['value'], f['value'])

    def recurse_group(self, mdkey, data):
        self.recurse_for_field(data['field'])
        self.recurse_group(data['group'])

    def metadataValueForKey(self, mdkey, meta):
        for item_data in meta:
            for ts in item_data['metadata']['timespan']:
                rtn = self.recurse_for_field(mdkey, ts['field'])
                if rtn is not None:
                    return rtn

                for g in ts['group']:
                    rtn = self.recurse_group(mdkey,g)
                    if rtn is not None:
                        return rtn

    def _find_group(self,groupname,meta):
        if not 'group' in meta:
            return None

        for g in meta['group']:
            if g['name'] == groupname:
                return g
            self._find_group(groupname,g)

    def metadataValueInGroup(self, groupname, mdkey, meta):
        for item_data in meta:
            for ts in item_data['metadata']['timespan']:
                group = self._find_group(groupname, ts)
                if group is None:
                    raise ValueError("Could not find group {0}".format(groupname))
                for f in group['field']:
                    if f['name'] == mdkey:
                        rtn = map(lambda x: x['value'],f['value'])
                        if len(rtn)==1:
                            return rtn[0]
                        else:
                            return rtn
        raise ValueError("Could not find metadata key {0}".format(mdkey))

    def return_string(self, tagname, *args):
        display = 0

        context = args[1]
        item = context['item']
        itemid = item.getId()

        from portal.vidispine.iitem import ItemHelper
        from pprint import pprint

        ith = ItemHelper()

        res = ith.getItemMetadata(itemid)
        #pprint(res)

        #print "gnm_external_archive_external_archive_status = {0}".format(self.metadataValueInGroup('ExternalArchiveRequest','gnm_external_archive_external_archive_status',res['item']))

        test_value = self.metadataValueInGroup('ExternalArchiveRequest','gnm_external_archive_external_archive_status',res['item'])
        path = self.metadataValueInGroup('ExternalArchiveRequest','gnm_external_archive_external_archive_path',res['item'])

        if test_value == archive_test_value:
            display = 1

        if display == 1:
            return {'guid':self.plugin_guid, 'template':'gearbox_menu.html', 'context' : {'itemid':itemid, 'path':path} }


GNMAWSGRpluginblock = GNMAWSGRGearboxMenuPlugin()

class GNMAWSGRCollectionGearboxMenuPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        self.name = "CollectionViewDropdown"
        self.plugin_guid = "71A4C13A-A116-4DAD-A801-DCC470BB2D7D"
        log.debug("Initiated GNMAWSGRCollectionGearboxMenuPlugin")

    def recurse_for_field(self, mdkey, data):
        for f in data:
            if f['name'] == mdkey:
                return map(lambda x: x['value'], f['value'])

    def recurse_group(self, mdkey, data):
        self.recurse_for_field(data['field'])
        self.recurse_group(data['group'])

    def metadataValueForKey(self, mdkey, meta):
        for item_data in meta:
            for ts in item_data['metadata']['timespan']:
                rtn = self.recurse_for_field(mdkey, ts['field'])
                if rtn is not None:
                    return rtn

                for g in ts['group']:
                    rtn = self.recurse_group(mdkey,g)
                    if rtn is not None:
                        return rtn

    def _find_group(self,groupname,meta):
        if not 'group' in meta:
            return None

        for g in meta['group']:
            if g['name'] == groupname:
                return g
            self._find_group(groupname,g)

    def metadataValueInGroup(self, groupname, mdkey, meta):
        for item_data in meta:
            for ts in item_data['metadata']['timespan']:
                group = self._find_group(groupname, ts)
                if group is None:
                    raise ValueError("Could not find group {0}".format(groupname))
                for f in group['field']:
                    if f['name'] == mdkey:
                        rtn = map(lambda x: x['value'],f['value'])
                        if len(rtn)==1:
                            return rtn[0]
                        else:
                            return rtn
        raise ValueError("Could not find metadata key {0}".format(mdkey))

    def return_string(self, tagname, *args):
        display = 0
        from portal.vidispine.iitem import ItemHelper
        from pprint import pprint

        context = args[1]
        collection = context['collection']
        content = collection.getItems()
        collid = collection.getId()

        #pprint(content[0].getId())

        for data in content:

            ith = ItemHelper()
            res = ith.getItemMetadata(data.getId())
            #pprint(data.getId())
            try:
                test_value = self.metadataValueInGroup('ExternalArchiveRequest','gnm_external_archive_external_archive_status',res['item'])
            except StandardError as e:
                log.error(str(e))
                raise
            if test_value == archive_test_value:
                display = 1

        if display == 1:
            return {'guid':self.plugin_guid, 'template':'collection_gearbox_menu.html', 'context' : {'collection':collid, 'res':''} }

GNMAWSGRCollectionpluginblock = GNMAWSGRCollectionGearboxMenuPlugin()


class GNMAWSGRBinGearboxMenuPlugin(Plugin):
    implements(IPluginBlock)

    def __init__(self):
        self.name = "MediaBinDropdown"
        self.plugin_guid = "FFCF6DC2-A88F-474A-A2FE-2C38440E3C85"
        log.debug("Initiated GNMAWSGRBinGearboxMenuPlugin")

    def return_string(self, tagname, *args):
        display = 1

        mediabin = getBinInfo()

        if display == 1:
            return {'guid':self.plugin_guid, 'template':'bin_gearbox_menu.html', 'context' : {'mediabin':mediabin} }

GNMAWSGRBinpluginblock = GNMAWSGRBinGearboxMenuPlugin()

