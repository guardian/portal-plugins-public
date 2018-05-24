import unittest2
from mock import MagicMock, patch, call
import json
import os
from django.core.management import execute_from_command_line
from django.conf import settings


class TestFindCategories(unittest2.TestCase):
    from helpers import MockResponse
    def test_find_categories(self):
        """
        find_categories should return a list of categories
        :return:
        """
        testdoc = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ItemListDocument xmlns="http://xml.vidispine.com/schema/vidispine">
    <hits>1691985</hits>
    <facet>
        <field>gnm_asset_category</field>
        <count fieldValue="Rushes">1165113</count>
        <count fieldValue="Completed Project">169266</count>
        <count fieldValue="HoldingImage">41071</count>
    </facet>
</ItemListDocument>"""

        with patch('requests.put', return_value=self.MockResponse(200, testdoc)):
            from portal.plugins.gnmplutostats.categoryscanner import find_categories
            result = find_categories()
            self.assertEqual(result, ['Rushes','Completed Project', 'HoldingImage'])


class TestProcessResultCategory(unittest2.TestCase):
    maxDiff = None

    def test_to_json(self):
        from portal.plugins.gnmplutostats.categoryscanner import ProcessResultCategory
        cat = ProcessResultCategory()
        cat.storage_sum = {
            'VX-1': 34634.34,
            'VX-2': 785.2,
            'VX-4': 923824.21
        }

        result = cat.to_json(category_name="test category", is_attached=True)
        expected_result = {u"category_name": u"test category", "storage_data": [{"storage_id": "VX-4", "size_used_gb": 923824.21}, {"storage_id": "VX-1", "size_used_gb": 34634.34}, {"storage_id": "VX-2", "size_used_gb": 785.2}], "is_attached": True}

        self.assertDictEqual(expected_result,json.loads(result))


class TestUpdateCategorySizeParallel(unittest2.TestCase):
    @classmethod
    def setUpClass(cls):
        if settings.DATABASES['default']['NAME']=="":
            raise ValueError("tests misconfigured, need a local database path")

        execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        execute_from_command_line(['manage.py', 'loaddata', 'parallel_tasks.yaml'])

    @classmethod
    def tearDownClass(cls):
        pass

    class MockTaskData(object):
        def __init__(self,task_id):
            self.task_id = task_id

    def test_parallel_scan_normal(self):
        """
        update_category_size_parallel should create a ParallelScanJob, a ParallelScanStep for each page and trigger tasks to run them
        :return:
        """
        from portal.plugins.gnmplutostats.models import ParallelScanStep, ParallelScanJob

        mock_task_data = self.MockTaskData("45523ce3-5171-496f-929f-8c6cfa9584fb")
        with patch('portal.plugins.gnmplutostats.tasks.scan_category_page_parallel.apply_async', return_value=mock_task_data) as mock_trigger_task:
            with patch('portal.plugins.gnmplutostats.categoryscanner.get_total_hits', return_value=123) as mock_get_total_hits:
                from portal.plugins.gnmplutostats.categoryscanner import update_category_size_parallel

                result = update_category_size_parallel("test")
                mock_get_total_hits.assert_called_once()

                j = ParallelScanJob.objects.get(job_desc="CategorySizeParallel",status="WAITING")
                self.assertEqual(j.items_to_scan,123)
                self.assertEqual(j.pages,4)

                self.assertEqual(mock_trigger_task.call_count, 4)
                steps = ParallelScanStep.objects.filter(master_job=j)
                self.assertEqual(len(steps), 4)

                mock_trigger_task.assert_has_calls([
                    call(kwargs={'step_id': steps[0].pk},queue="celery"),
                    call(kwargs={'step_id': steps[1].pk},queue="celery"),
                    call(kwargs={'step_id': steps[2].pk},queue="celery"),
                    call(kwargs={'step_id': steps[3].pk},queue="celery"),
                ],any_order=True)

                self.assertEqual(steps[0].status,"WAITING")
                self.assertEqual(steps[0].start_at,1)
                self.assertEqual(steps[0].end_at,40)
                self.assertEqual(steps[1].status,"WAITING")
                self.assertEqual(steps[1].start_at,41)
                self.assertEqual(steps[1].end_at,80)
                self.assertEqual(steps[2].status,"WAITING")
                self.assertEqual(steps[2].start_at,81)
                self.assertEqual(steps[2].end_at,120)
                self.assertEqual(steps[3].status,"WAITING")
                self.assertEqual(steps[3].start_at,121)
                self.assertEqual(steps[3].end_at,160)


class TestSumSteps(unittest2.TestCase):
    def test_sum_steps(self):
        """
        sum_steps should add together the total amounts for storages across a group of job steps
        :return:
        """
        from portal.plugins.gnmplutostats.categoryscanner import ProcessResultCategory, sum_steps
        from portal.plugins.gnmplutostats.models import ParallelScanStep

        results = [
            ProcessResultCategory(initial_data={'VX-1': 1, 'VX-2': 2, 'VX-3': 3},metadata={'category_name': "Test", 'is_attached': True}),
            ProcessResultCategory(initial_data={'VX-1': 4, 'VX-2': 5, 'VX-3': 6},metadata={'category_name': "Test", 'is_attached': True}),
            ProcessResultCategory(initial_data={'VX-1': 7, 'VX-2': 8, 'VX-3': 9},metadata={'category_name': "Test", 'is_attached': False}),
        ]

        steps = map(lambda result:
                    ParallelScanStep(master_job_id=1,
                                     status="COMPLETED",
                                     search_param="Test",
                                     start_at=1,
                                     end_at=20,
                                     result=result.to_json()    #use the values we already set
                                     ), results)

        final_result = sum_steps(steps)
        self.assertDictEqual(final_result['attached'].storage_sum,{
            'VX-1': 5,
            'VX-2': 7,
            'VX-3': 9
        })
        self.assertDictEqual(final_result['unattached'].storage_sum,{
            'VX-1': 7,
            'VX-2': 8,
            'VX-3': 9
        })
