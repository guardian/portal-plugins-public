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
execute_manager(django_test_settings,['manage.py','syncdb', "--noinput"])
execute_manager(django_test_settings,['manage.py','migrate', "--noinput"])



class TestTasks(unittest.TestCase):

    def test_human_friendly(self):
        from gnmpagerduty.tasks import human_friendly

        self.assertEqual(human_friendly(8589934592),"8.0GiB")
        self.assertEqual(human_friendly(17592186044416),"16.0TiB")
        self.assertEqual(human_friendly(28037546508288),"25.5TiB")

    def test_return_percentage(self):
        from gnmpagerduty.tasks import return_percentage

        self.assertEqual(return_percentage(100, 50), 50)

    def test_get_system_type_cached(self):
        from gnmpagerduty.tasks import get_system_type

        with patch('django.core.cache.cache.get', return_value='Live') as mock_cache:
            with patch('gnmpagerduty.tasks.make_vidispine_request') as mock_request:
                result = get_system_type()
                self.assertEqual(result,'Live')
                mock_request.assert_not_called()
                mock_cache.assert_called_once_with('gnmpagerduty_system_type')

    def test_get_system_type_not_cached(self):
        from gnmpagerduty.tasks import get_system_type

        with patch('django.core.cache.cache.get', return_value=None) as mock_cache:
            with patch('gnmpagerduty.tasks.make_vidispine_request', return_value=({}, 'site contains KP')) as mock_request:
                result = get_system_type()
                self.assertEqual(result,'Live')
                mock_request.assert_called_once()
                mock_cache.assert_called_once()

    TEST_STORAGE_DATA = {
        'name': 'VX-1234',
        'freeCapacity': 12345,
        'capacity': 456780,
        'contentDict': {
            'name': 'Kevin',
        }
    }

    def test_storage_below_safelevel(self):
        from gnmpagerduty.models import IncidentKeys

        mock_key = IncidentKeys()

        with patch('gnmpagerduty.tasks.get_system_type', return_value="Live") as mocksystype:
            with patch('gnmpagerduty.tasks.notify_pagerduty', return_value={'incident_key': 'blahblah'}) as mocknotify:
                from gnmpagerduty.tasks import storage_below_safelevel
                storage_below_safelevel(mock_key, self.TEST_STORAGE_DATA)

                mocknotify.assert_called_once_with('Storage Kevin lacks sufficient free space. It is 97% full.',
                                                   'trigger',
                                                   '',
                                                   free_capacity='12.1KiB',
                                                   storage_name='Kevin',
                                                   system_type='Live',
                                                   vidis_id='VX-1234')

                mocknotify.reset_mock()
                mock_key.incident_key = "somethingsomething"
                storage_below_safelevel(mock_key,self.TEST_STORAGE_DATA)
                mocknotify.assert_not_called()
        mock_key.delete()

    def test_storage_above_safelevel(self):
        from gnmpagerduty.models import IncidentKeys

        mock_key = IncidentKeys()

        with patch('gnmpagerduty.tasks.get_system_type', return_value="Live") as mocksystype:
            with patch('gnmpagerduty.tasks.notify_pagerduty', return_value={'incident_key': 'blahblah'}) as mocknotify:
                from gnmpagerduty.tasks import storage_above_safelevel
                mock_key.incident_key = "somethingsomething"
                storage_above_safelevel(mock_key, self.TEST_STORAGE_DATA)

                mocknotify.assert_called_once_with('Storage Kevin no longer lacks sufficient free space. It is 97% full.',
                                                   'resolve',
                                                   'somethingsomething',
                                                   free_capacity='12.1KiB',
                                                   storage_name='Kevin',
                                                   system_type='Live',
                                                   vidis_id='VX-1234')


                mocknotify.reset_mock()
                mock_key.incident_key = ""
                storage_above_safelevel(mock_key,self.TEST_STORAGE_DATA)
                mocknotify.assert_not_called()
        mock_key.delete()

    class MockCeleryApp(object):
        """
        mock object to fake celery call for checking how many instances are running
        """
        def __init__(self, instance_count):
            self.instance_count=instance_count
            self.control = self.MockInternalControl(instance_count)

        class MockInternalControl(object):
            def __init__(self, instance_count):
                self.instance_count = instance_count

            def inspect(self):
                return self.MockInternalInspect(self.instance_count)

            class MockInternalInspect(object):
                def __init__(self, instance_count):
                    self.instance_count = instance_count

                def active(self):
                    rtn = ""
                    for n in range(0,self.instance_count):
                        rtn+="check_storage "
                    return rtn

    class MockObject(object):
        """
        fakes a .__dict__() method on something that is already a dict
        """
        def __init__(self,obj):
            self.obj = obj

        @property
        def __dict__(self):
            return self.obj

    def test_check_storages_above(self):
        """
        tests the check_storages function when the storage is above the limit, i.e. fine
        :return:
        """
        mockceleryapp = self.MockCeleryApp(1)
        from gnmpagerduty.models import StorageData

        test_storagedata = StorageData()
        test_storagedata.storage_id=self.TEST_STORAGE_DATA['name']
        test_storagedata.trigger_size=100
        test_storagedata.save()

        with patch('gnmvidispine.vs_storage.VSStoragePathMap', return_value={'/some/path/to': self.MockObject(self.TEST_STORAGE_DATA)}) as mock_path_map:
            with patch('gnmpagerduty.tasks.storage_above_safelevel') as mock_abovesafelevel:
                from gnmpagerduty.tasks import check_storage

                result = check_storage(celery_app=mockceleryapp)
                self.assertEqual(result, "No storages are under their thresholds.")
                mock_path_map.assert_called_once()
                mock_abovesafelevel.assert_called_once()
        test_storagedata.delete()

    def test_check_storages_below(self):
        """
        tests the check_storages function when the storage is below the limit, i.e. in trouble.
        :return:
        """
        mockceleryapp = self.MockCeleryApp(1)
        from gnmpagerduty.models import StorageData

        test_storagedata = StorageData()
        test_storagedata.storage_id=self.TEST_STORAGE_DATA['name']
        test_storagedata.trigger_size=100000
        test_storagedata.save()

        with patch('gnmvidispine.vs_storage.VSStoragePathMap', return_value={'/some/path/to': self.MockObject(self.TEST_STORAGE_DATA)}) as mock_path_map:
            with patch('gnmpagerduty.tasks.storage_below_safelevel') as mock_belowsafelevel:
                from gnmpagerduty.tasks import check_storage

                result = check_storage(celery_app=mockceleryapp)
                self.assertEqual(result, "Storages below threshold: Kevin")
                mock_path_map.assert_called_once()
                mock_belowsafelevel.assert_called_once()
        test_storagedata.delete()


class TestNotifyPagerduty(unittest.TestCase):
    class FakeResponse(object):
        def __init__(self, code, content):
            self.status_code = code
            self.content=content
            self.headers={}

        def json(self):
            import json
            return json.loads(self.content)

    def test_notify_pagerduty(self):
        import json
        with patch('requests.post',return_value=self.FakeResponse(200,json.dumps({'incident_key': 'blahblah'}))) as mockpost:
            from gnmpagerduty.tasks import notify_pagerduty

            result = notify_pagerduty("this is a test message",
                             "trigger",
                             "",
                             vidis_id="VX-123",
                             storage_name="fred",
                             free_capacity=512436,
                             system_type="test")

            self.assertEqual(result,{'incident_key': 'blahblah'})
            mockpost.assert_called_once_with('https://events.pagerduty.com/generic/2010-04-15/create_event.json',
                                             data='{"details": {"System Type": "test", "Vidispine ID": "VX-123", "Name": "fred", "Free Capacity": 512436}, "incident_key": "", "service_key": "blahblahblahblah", "event_type": "trigger", "description": "this is a test message"}')

    def test_pagerduty_exception(self):
        import json
        with patch('requests.post',return_value=self.FakeResponse(503,json.dumps({'incident_key': 'blahblah'}))) as mockpost:
            from gnmpagerduty.tasks import notify_pagerduty,HttpError

            def testfunc():
                notify_pagerduty("this is a test message",
                                 "trigger",
                                 "",
                                  vidis_id="VX-123",
                                  storage_name="fred",
                                  free_capacity=512436,
                                  system_type="test")
            self.assertRaises(HttpError,testfunc)