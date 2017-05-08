from __future__ import absolute_import
from django.core.management import execute_manager
import unittest
from mock import patch, MagicMock
from os import environ, unlink
import os.path

environ["CI"] = "True"  #simulate a CI environment even if we're not in one, this will stop trying to import portal-specific stuff
#which breaks the tests
import gnmpagerduty.tests.django_test_settings as django_test_settings

environ["DJANGO_SETTINGS_MODULE"] = "gnmpagerduty.tests.django_test_settings"
if os.path.exists(django_test_settings.DATABASES['default']['NAME']):
    unlink(django_test_settings.DATABASES['default']['NAME'])
execute_manager(django_test_settings,['manage.py','syncdb'])
execute_manager(django_test_settings,['manage.py','migrate'])


class TestViews(unittest.TestCase):

    class MockObject(object):
        """
        fakes a .__dict__() method on something that is already a dict
        """
        def __init__(self,obj):
            self.obj = obj

        @property
        def __dict__(self):
            return self.obj

    TEST_STORAGE_DATA = {
        'name': 'VX-1234',
        'freeCapacity': 12345,
        'capacity': 456780,
        'contentDict': {
            'name': 'Kevin',
        }
    }

    def test_get_context_data(self):
        from gnmpagerduty.views.ConfigAlertsView import get_context_data
        from gnmpagerduty.models import StorageData

        model = StorageData

        with patch('gnmvidispine.vs_storage.VSStoragePathMap', return_value={'/some/path/to': self.MockObject(self.TEST_STORAGE_DATA)}) as mock_path_map:
            self.assertEqual(get_context_data(self, modelready=model),"Fix me")

