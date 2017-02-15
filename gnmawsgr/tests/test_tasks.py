# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from django.core.management import execute_manager
import unittest2
from mock import MagicMock, patch, call
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


class TestTasks(unittest2.TestCase):
    def test_filepath_to_uri(self):
        from gnmawsgr.tasks import filepath_to_uri
        filepath="/path/to/simplefile.ext"
        self.assertEqual(filepath_to_uri(filepath),"file://" + filepath)

        filepath="/path/to/file with spaces.ext"
        self.assertEqual(filepath_to_uri(filepath),"file:///path/to/file%20with%20spaces.ext")

        filepath="/path/to/file with ümlauts.ext"
        self.assertEqual(filepath_to_uri(filepath),"file:///path/to/file%20with%20%C3%BCmlauts.ext")

    class fake_job(object):
        def __init__(self,fake_job_id,success=True,finished=True,error_message=""):
            self.name = fake_job_id
            self._success=success
            self._finished=finished
            self.errorMessage=error_message

        def finished(self):
            return self._finished

        def didFail(self):
            return not self._success

        def populate(self, itemid):
            pass

        def status(self):
            if self._success and self._finished:
                return "SUCCESS"
            elif self._finished:
                return "FAILURE"
            else:
                return "RUNNING"

    def test_post_restore_actions(self):
        from gnmawsgr.tasks import post_restore_actions, check_import_completed
        from gnmvidispine.vs_item import VSItem
        from gnmawsgr.models import RestoreRequest
        from django.conf import settings

        check_import_completed.apply_async = MagicMock()

        rq = RestoreRequest()
        rq.pk=5
        rq.item_id="VX-123"
        rq.import_job=""
        rq.attempts=0
        rq.status="IMPORTING"
        rq.save = MagicMock()

        i=VSItem(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
        i.import_to_shape = MagicMock(return_value=self.fake_job("VX-456"))

        post_restore_actions(i,rq,"/path/to/downloaded file location.mp4")

        check_import_completed.apply_async.assert_called_once()
        i.import_to_shape.assert_called_with(uri="file:///path/to/downloaded%20file%20location.mp4")
        self.assertEqual(rq.import_job,"VX-456")
        rq.save.assert_called_once()

    def test_check_import_completed(self):
        from gnmawsgr.tasks import check_import_completed
        from gnmawsgr.models import RestoreRequest
        from datetime import datetime

        rq = RestoreRequest()
        rq.requested_at = datetime.now()
        rq.item_id="VX-123"
        rq.import_job="VX-456"
        rq.attempts=0
        rq.status="IMPORTING"
        rq.save()

        fakejob = self.fake_job("VX-456",success=True,finished=False)
        fakejob.populate=MagicMock()

        with patch('gnmvidispine.vs_item.VSItem.set_metadata') as mockset:
            with patch('gnmvidispine.vs_job.VSJob',return_value=fakejob) as mockjob:
                with patch('gnmawsgr.tasks.check_import_completed.apply_async') as mockasync:
                    check_import_completed(rq.pk)
                    fakejob.populate.assert_called_with("VX-456")
                    mockset.assert_not_called()
                    newrq = RestoreRequest.objects.get(pk=rq.pk)
                    self.assertEqual(newrq.status,"IMPORTING")
                    mockasync.assert_called_once_with((), {'requestid': rq.pk}, countdown=20)

            mockset.reset_mock()
            mockasync.reset_mock()
            fakejob = self.fake_job("VX-456",success=True,finished=True)
            fakejob.populate=MagicMock()
            with patch('gnmvidispine.vs_job.VSJob',return_value=fakejob) as mockjob:
                check_import_completed(rq.pk)
                fakejob.populate.assert_called_with("VX-456")
                mockset.assert_called_once_with({
                    'gnm_asset_status': 'Ready for Editing (from Archive)',
                    'gnm_external_archive_external_archive_status': "Restore Completed",
                })
                newrq = RestoreRequest.objects.get(pk=rq.pk)
                self.assertEqual(newrq.status,"COMPLETED")
                mockasync.assert_not_called()

            mockset.reset_mock()
            mockasync.reset_mock()
            fakejob = self.fake_job("VX-456", success=False,finished=True,error_message="it blew up kaboom")
            fakejob.populate=MagicMock()
            with patch('gnmvidispine.vs_job.VSJob',return_value=fakejob) as mockjob:
                check_import_completed(rq.pk)
                fakejob.populate.assert_called_with("VX-456")
                mockset.assert_called_once_with({'gnm_external_archive_external_archive_status': 'Restore Failed'})
                newrq = RestoreRequest.objects.get(pk=rq.pk)
                self.assertEqual(newrq.status,"IMPORT_FAILED")
                self.assertEqual(newrq.failure_reason,"it blew up kaboom")
                mockasync.assert_not_called()
