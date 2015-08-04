from django.forms import *


class ShowSearchForm(Form):
    only_named = BooleanField(required=False)
    only_with_storage_rules = BooleanField(required=False)
    only_auto_refreshing = BooleanField(required=False)


class ConfigurationForm(Form):
    library_id = CharField(max_length=32)
    library_owner = CharField(max_length=255)
    auto_refresh = BooleanField(required=False)
    update_mode = ChoiceField(choices=[
        ('REPLACE','REPLACE'),
        ('MERGE','MERGE'),
        ('TRANSIENT','TRANSIENT'),
    ])
    search_definition = CharField(max_length=65536,widget=Textarea())
    storage_rule_definition = CharField(max_length=65536, widget=Textarea())

    def __init__(self, lib, *args, **kwargs):
        from .VSLibrary import VSLibrary
        import xml.etree.ElementTree as ET
        from xml.dom import minidom

        import logging
        initial = {}
        if isinstance(lib,VSLibrary):
            initial['library_id'] = lib.vsid
            initial['library_owner'] = lib.owner
            initial['auto_refresh'] = lib.autoRefresh
            initial['update_mode'] = lib.updateMode
            initial['search_definition'] = minidom.parseString(ET.tostring(lib.query,encoding="UTF-8")).toprettyxml()
            initial['storage_rule_definition'] = None
            try:
                initial['storage_rule_definition'] = minidom.parseString(ET.tostring(lib.storagerule,encoding="UTF-8")).toprettyxml()
            except StandardError as e:
                logging.warning(e)

        super(ConfigurationForm,self).__init__(*args,initial=initial,**kwargs)

