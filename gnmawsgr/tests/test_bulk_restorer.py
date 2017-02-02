from __future__ import absolute_import
import unittest2
from mock import MagicMock, patch
import httplib
import base64
import logging
import tempfile
from os import environ


environ["CI"] = "True"  #simulate a CI environment even if we're not in one, this will stop trying to import portal-specific stuff


class TestBulkRestorer(unittest2.TestCase):
    def test_metadata_remapping(self):
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
        