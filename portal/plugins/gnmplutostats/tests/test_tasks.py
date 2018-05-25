import django.test
from mock import MagicMock, patch
import os
from django.core.management import execute_from_command_line
from django.conf import settings


class TestScanCategoryPageParallel(django.test.TestCase):
    @classmethod
    def setUpClass(cls):
        if settings.DATABASES['default']['NAME']=="":
            raise ValueError("tests misconfigured, need a local database path")
        # if os.path.exists(settings.DATABASES['default']['NAME']):
        #     os.unlink(settings.DATABASES['default']['NAME'])

        execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        execute_from_command_line(['manage.py', 'loaddata', 'parallel_tasks.yaml'])

    @classmethod
    def tearDownClass(cls):
        pass

    def test_parallel_scan_normal(self):
        """
        scan_category_page_parallel should perform a scan and store the results as json in the database
        :return:
        """
        from portal.plugins.gnmplutostats.categoryscanner import ProcessResultCategory
        from portal.plugins.gnmplutostats.models import ParallelScanStep
        import json

        fake_data = {
            'attached': ProcessResultCategory(),
            'unattached': ProcessResultCategory()
        }
        fake_data['attached'].storage_sum = {'VX-1': 34634.34,'VX-2': 785.2,'VX-4': 923824.21}
        fake_data['unattached'].storage_sum = {'VX-1': 234.34,'VX-2': 543.2,'VX-4': 734575.21}

        with patch('portal.plugins.gnmplutostats.categoryscanner.process_next_page', return_value=fake_data) as mock_process_next_page:
            with patch('portal.plugins.gnmplutostats.tasks.scan_category_page_parallel.apply_async') as mock_apply:
                from portal.plugins.gnmplutostats.tasks import scan_category_page_parallel

                scan_category_page_parallel(step_id=1)
                mock_process_next_page.assert_called_once()
                self.assertEqual(mock_process_next_page.call_args[0][0],"Test")
                self.assertEqual(mock_process_next_page.call_args[0][2],1)
                self.assertEqual(mock_process_next_page.call_args[0][3],39)

                saved_record = ParallelScanStep.objects.get(pk=1)
                self.assertEqual(saved_record.status,"COMPLETED")
                self.assertEqual(saved_record.last_error,None)
                self.assertEqual(saved_record.retry_count, 1)
                self.assertEqual(json.loads(saved_record.result),[{u'storage_data': [{u'size_used_gb': 923824.21, u'storage_id': u'VX-4'}, {u'size_used_gb': 34634.34, u'storage_id': u'VX-1'}, {u'size_used_gb': 785.2, u'storage_id': u'VX-2'}], u'is_attached': True, u'category_name': u'Test'}, {u'storage_data': [{u'size_used_gb': 734575.21, u'storage_id': u'VX-4'}, {u'size_used_gb': 234.34, u'storage_id': u'VX-1'}, {u'size_used_gb': 543.2, u'storage_id': u'VX-2'}], u'is_attached': False, u'category_name': u'Test'}])
                mock_apply.assert_not_called()
    class FakeResponse(object):
        def __init__(self,status_code,text,headers):
            self.status_code=status_code
            self.text=text
            self.headers=headers

    def test_parallel_scan_error(self):
        """
        scan_category_page_parallel should log any exception that occurs and reschedule itself
        :return:
        """
        from portal.plugins.gnmplutostats.categoryscanner import ProcessResultCategory
        from portal.plugins.gnmplutostats.models import ParallelScanStep
        from portal.plugins.gnmplutostats.exceptions import HttpError

        fake_data = {
            'attached': ProcessResultCategory(),
            'unattached': ProcessResultCategory()
        }
        fake_data['attached'].storage_sum = {'VX-1': 34634.34,'VX-2': 785.2,'VX-4': 923824.21}
        fake_data['unattached'].storage_sum = {'VX-1': 234.34,'VX-2': 543.2,'VX-4': 734575.21}

        fake_error = HttpError(self.FakeResponse(400,"My hovercraft is full of eels",{}))

        with patch('portal.plugins.gnmplutostats.categoryscanner.process_next_page', side_effect=fake_error) as mock_process_next_page:
            with patch('portal.plugins.gnmplutostats.tasks.scan_category_page_parallel.apply_async') as mock_apply:
                from portal.plugins.gnmplutostats.tasks import scan_category_page_parallel

                with self.assertRaises(HttpError):
                    scan_category_page_parallel(step_id=2)
                mock_process_next_page.assert_called_once()
                self.assertEqual(mock_process_next_page.call_args[0][0],"Test")
                self.assertEqual(mock_process_next_page.call_args[0][2],41)
                self.assertEqual(mock_process_next_page.call_args[0][3],39)

                saved_record = ParallelScanStep.objects.get(pk=2)
                self.assertEqual(saved_record.status,"FAILED")
                self.assertNotEqual(saved_record.last_error,None)
                self.assertEqual(saved_record.retry_count, 1)
                mock_apply.assert_called_once_with(kwargs={'step_id': 2},queue="celery",countdown=2)