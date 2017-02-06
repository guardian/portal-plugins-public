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
        
        #pprint(remapped_data)
        self.assertDictContainsSubset(remapped_document,remapped_data['fields'])

    def test_1initiate(self):   #the 1 ensures that this test gets run first, otherwise the id checks below fail
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
            
        u.username = "admin"
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
    
        u.username = "admin"
        u.is_superuser = True
        
        with patch("gnmawsgr.bulk_restorer.BulkRestorer._bulk_restore_main") as cm:
            record_id = r.initiate_bulk(u,"KP-1234",inTest=True)
            r.bulk_restore_main(record_id)
            
        cm.assert_called_once()
        
    def test_process_item_valid(self):
        """
        test the item process function
        :return:
        """
        from gnmawsgr.bulk_restorer import BulkRestorer
        from gnmawsgr.models import BulkRestore
        from django.contrib.auth.models import User
        from .FakeSettings import settings
        
        with patch("django.conf.settings", settings()):
            r = BulkRestorer()
            u = User()
        u.username = "admin"
        u.is_superuser = True
        
        request_id = r.initiate_bulk(u, 'VX-1111', inTest=True)
        request_model = BulkRestore.objects.get(pk=request_id)
        
        with patch("gnmawsgr.tasks.glacier_restore") as restorecall:
            with patch("gnmvidispine.vs_item.VSItem.set_metadata") as setmdcall:
                restorecall.delay = MagicMock()
                fakemeta_valid = {
                    'itemId': 'VX-1234',
                    'fields': {
                        'gnm_external_archive_external_archive_request': ['Requested Restore'],
                        'gnm_external_archive_external_archive_status': ['Archived'],
                        'gnm_external_archive_external_archive_report': [""]
                    }
                }
                r.process_item(fakemeta_valid,request_model)
        restorecall.delay.assert_called_once_with(1,'VX-1234')
        setmdcall.assert_called_once()  #hard to check items as one of the md values includes a timestamp!

    def test_process_item_missingfields(self):
        """
        test the item process function
        :return:
        """
        from gnmawsgr.bulk_restorer import BulkRestorer
        from gnmawsgr.models import BulkRestore
        from django.contrib.auth.models import User
        from .FakeSettings import settings
        
        with patch("django.conf.settings", settings()):
            r = BulkRestorer()
            u = User()
        u.username = "admin"
        u.is_superuser = True
        
        request_id = r.initiate_bulk(u, 'VX-1111', inTest=True)
        request_model = BulkRestore.objects.get(pk=request_id)
        
        with patch("gnmawsgr.tasks.glacier_restore") as restorecall:
            with patch("gnmvidispine.vs_item.VSItem.set_metadata") as setmdcall:
                restorecall.delay = MagicMock()
                fakemeta_valid = {
                    'itemId': 'VX-1234',
                    'fields': {
                        'gnm_external_archive_external_archive_report' : [""]
                    }
                }
                with self.assertRaises(KeyError):
                    r.process_item(fakemeta_valid, request_model)
        restorecall.delay.assert_not_called()
        setmdcall.assert_not_called()  #nothing is recorded to the item in this case
    
    class FakeFuture(object):
        def __init__(self):
            import json
            from .testdata import raw_item_json
            self.data = json.loads(raw_item_json)
            
        def waitfor_json(self):
            return self.data
        
    class FakeWrappedSearch(object):
        def __init__(self, params, pagesize=10):
            pass
        
        def execute(self, start_at=0, fieldlist=[]):
            return TestBulkRestorer.FakeFuture()
        
    def test_get_searchpages(self):
        """
        test the run-search function
        :return:
        """
        from pprint import pprint
        
        with patch('gnmawsgr.vsmixin.VSWrappedSearch', self.FakeWrappedSearch) as wrappedsearch:
            wrappedsearch.execute = MagicMock(return_value = TestBulkRestorer.FakeFuture())
            
            from gnmawsgr.bulk_restorer import BulkRestorer
            from gnmawsgr.models import BulkRestore
            from django.contrib.auth.models import User
            from .FakeSettings import settings
        
            with patch("django.conf.settings", settings()):
                r = BulkRestorer()
                u = User()
            u.username = "admin"
            u.is_superuser = True
        
            request_id = r.initiate_bulk(u, 'VX-1111', inTest=True)
            request_model = BulkRestore.objects.get(pk=request_id)
            
            r.process_item = MagicMock()
            for item in r._get_searchpages(request_model):
                self.assertEqual(item['fields']['user'],[u'admin'])
                self.assertEqual(item['fields']['title'], [u'T\xe9st with \xfcmlauts'])
                self.assertEqual(item['fields']['gnm_master_website_trail'], [u'Holy Guacamole!'])
        wrappedsearch.execute.assert_called()
        self.assertEqual(wrappedsearch.execute.call_count,2)