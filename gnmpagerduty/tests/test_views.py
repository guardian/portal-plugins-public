from __future__ import absolute_import
from os import environ, unlink
environ["DJANGO_SETTINGS_MODULE"] = "gnmpagerduty.tests.django_test_settings"
from django.core.management import execute_manager
import django.test
import unittest
from mock import patch, MagicMock
import os.path

environ["CI"] = "True"  #simulate a CI environment even if we're not in one, this will stop trying to import portal-specific stuff
#which breaks the tests
import gnmpagerduty.tests.django_test_settings as django_test_settings

if os.path.exists(django_test_settings.DATABASES['default']['NAME']):
    unlink(django_test_settings.DATABASES['default']['NAME'])
execute_manager(django_test_settings,['manage.py','syncdb',"--noinput"])
execute_manager(django_test_settings,['manage.py','migrate',"--noinput"])


class TestViews(django.test.TestCase):

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
        from django.contrib.auth.models import User
        from django.http import HttpResponse
        import logging

        logging.basicConfig(level=logging.DEBUG)
        u = User(first_name="test",last_name="test",username="test")
        u.set_password("nothing")
        u.is_active=True
        u.is_superuser=False
        u.save()

        self.client.login(username="test", passwd="nothing")

        with patch('gnmpagerduty.views.VSStoragePathMap', return_value={'/some/path/to': self.MockObject(self.TEST_STORAGE_DATA)}) as mock_path_map:
            with patch('gnmpagerduty.views.ConfigAlertsView.render_to_response', return_value=HttpResponse()) as mock_render:
                result = self.client.get('/alerts/')
                self.assertEqual(result.status_code,200)

                mock_render.assert_called_once()
                self.assertDictContainsSubset({'map': [{'contentDict': {'name': 'Kevin'}, 'triggerSize': 0, 'freeCapacity': 12345, 'capacity': 456780, 'name': 'VX-1234'}]}, mock_render.call_args[0][0])
