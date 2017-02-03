from __future__ import absolute_import
from django.core.management import execute_manager
import unittest2
from mock import MagicMock, patch
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


class TestBulkRestorer(unittest2.TestCase):
    def test_metadata_remapping(self):
        """
        test metadata remapper/cruncher
        :return:
        """
        from gnmawsgr.bulk_restorer import BulkRestorer
        import json
        from pprint import pprint
        from .testdata import raw_item_json, remapped_document
        from .FakeSettings import settings
        
        with patch("django.conf.settings", settings()):
            r = BulkRestorer()
        
        content = json.loads(raw_item_json)
        
        remapped_data = r.remap_metadata(content['item'][0])
        
        pprint(remapped_data)
        self.assertDictContainsSubset(remapped_document,remapped_data['fields'])

    def test_initiate(self):
        """
        test ability to initate a bulk restore request
        :return:
        """
        from gnmawsgr.bulk_restorer import BulkRestorer
        from django.contrib.auth.models import User
        from .FakeSettings import settings
        from gnmawsgr.models import BulkRestore
        
        with patch("django.conf.settings", settings()):
            r = BulkRestorer()
            u = User()
            
        u.name = "admin"
        u.is_superuser= True
        
        first_id = r.initiate_bulk(u,"KP-1234",inTest=True)
        self.assertEqual(first_id,1)
        record = BulkRestore.objects.get(pk=first_id)
        self.assertEqual(record.username, "admin")
        self.assertEqual(record.parent_collection, "KP-1234")
        self.assertEqual(record.current_status, "Queued")
        
        second_id = r.initiate_bulk(u, "KP-5678", inTest=True)
        self.assertEqual(second_id,2)
        
        third_id = r.initiate_bulk(u,"KP-1234",inTest=True) #should return the ID of the first request
        self.assertEqual(third_id, 1)
        
    def test_restore_wrapper(self):
        """
        test the wrapper for bulk_restore_main
        :return:
        """
        from gnmawsgr.bulk_restorer import BulkRestorer
        from django.contrib.auth.models import User
        from .FakeSettings import settings
    
        with patch("django.conf.settings", settings()):
            r = BulkRestorer()
            u = User()
    
        u.name = "admin"
        u.is_superuser = True
        
        with patch("gnmawsgr.bulk_restorer.BulkRestorer._bulk_restore_main") as cm:
            record_id = r.initiate_bulk(u,"KP-1234",inTest=True)
            r.bulk_restore_main(record_id)
            
        cm.assert_called_once()