from __future__ import absolute_import
from django.core.management import execute_manager
import unittest2
from mock import MagicMock, patch, call
import httplib
import base64
import logging
import tempfile
from os import environ, system, unlink
import os.path

environ["CI"] = "True"  #simulate a CI environment even if we're not in one, this will stop trying to import portal-specific stuff
                        #which breaks the tests
import gnmawsgr.tests.django_test_settings as django_test_settings

environ["DJANGO_SETTINGS_MODULE"] = "gnmawsgr.tests.django_test_settings"
if(os.path.exists(django_test_settings.DATABASES['default']['NAME'])):
    unlink(django_test_settings.DATABASES['default']['NAME'])
execute_manager(django_test_settings,['manage.py','syncdb'])
execute_manager(django_test_settings,['manage.py','migrate'])


class TestInstaller(unittest2.TestCase):

    xml_field_response = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><MetadataFieldDocument xmlns="http://xml.vidispine.com/schema/vidispine"><name>gnm_external_archive_external_archive_status</name><type>string-exact</type><stringRestriction/><data><key>extradata</key><value>{"sortable": false, "name": "External Archive Status", "External Archive Request": {"required": false, "hideifnotset": false, "representative": false}, "pattern": null, "ExternalArchiveRequest": {"required": false, "hideifnotset": false, "representative": false}, "default": "Not In External Archive", "readonly": false, "values": [{"value": "Not In External Archive", "key": "Not In External Archive"}, {"value": "Upload in Progress", "key": "Upload in Progress"}, {"value": "Upload Failed", "key": "Upload Failed"}, {"value": "Awaiting Verification", "key": "Awaiting Verification"}, {"value": "Archived", "key": "Archived"}], "autoset": null, "externalid": "", "reusable": false, "type": "dropdown", "description": ""}</value></data><defaultValue>Not In External Archive</defaultValue><origin>VX</origin></MetadataFieldDocument>
    """
    updated_xml_body = """<ns0:MetadataFieldDocument xmlns:ns0="http://xml.vidispine.com/schema/vidispine"><ns0:name>gnm_external_archive_external_archive_status</ns0:name><ns0:type>string-exact</ns0:type><ns0:stringRestriction /><ns0:data><ns0:key>extradata</ns0:key><ns0:value>{"sortable": false, "name": "External Archive Status", "External Archive Request": {"required": false, "hideifnotset": false, "representative": false}, "pattern": null, "description": "", "ExternalArchiveRequest": {"required": false, "hideifnotset": false, "representative": false}, "default": "Not In External Archive", "readonly": false, "values": [{"key": "Not In External Archive", "value": "Not In External Archive"}, {"key": "Upload in Progress", "value": "Upload in Progress"}, {"key": "Upload Failed", "value": "Upload Failed"}, {"key": "Awaiting Verification", "value": "Awaiting Verification"}, {"key": "Archived", "value": "Archived"}, {"value": "choice one", "key": "choice one"}, {"value": "choice two", "key": "choice two"}], "autoset": null, "externalid": "", "type": "dropdown", "reusable": false}</ns0:value></ns0:data><ns0:defaultValue>Not In External Archive</ns0:defaultValue><ns0:origin>VX</ns0:origin></ns0:MetadataFieldDocument>"""

    def test_add_choices_to_field(self):
        from gnmawsgr.management.commands.install_glacierrestore import Command
        import httplib2
        fakeconn = httplib2.Http()
        
        c = Command()
        c._make_vidispine_request = MagicMock(return_value = ({'Content-Type': 'application/xml'}, self.xml_field_response,))
        
        c.add_choices_to_field("test_field",choices=["choice one", "choice two"],conn=fakeconn)
        
        c._make_vidispine_request.assert_has_calls([call(fakeconn,
                                                          "GET",
                                                          "/API/metadata-field/test_field?data=all",
                                                          body=None,
                                                          headers={'Accept': 'application/xml'}),
                                                    call(fakeconn,
                                                           "PUT",
                                                      "/API/metadata-field/test_field",
                                                      body=self.updated_xml_body,
                                                      headers={})
                                                    ],any_order=False)
