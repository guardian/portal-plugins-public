from __future__ import absolute_import
import django.test
from mock import MagicMock, patch
from django.core.management import execute_from_command_line
from django.core.urlresolvers import reverse, reverse_lazy
import os

execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
execute_from_command_line(['manage.py', 'migrate', '--noinput'])
execute_from_command_line(['manage.py', 'loaddata', 'fixtures/ImportJobs.yaml'])


class TestTasks(django.test.TestCase):
    fixtures = [
        'ImportJobs'
    ]

    def test_cleanup_old_importjobs(self):
        """
        cleanup_old_importjobs should purge out jobs older than 60 days
        :return:
        """
        from portal.plugins.gnmatomresponder.models import ImportJob
        from portal.plugins.gnmatomresponder.tasks import cleanup_old_importjobs
        #FIXME: should patch datetime.now() to always return the same value, for time being rely on fixture values being much
        #older than 60 days.
        self.assertEqual(ImportJob.objects.all().count(), 5)
        cleanup_old_importjobs()
        self.assertEqual(ImportJob.objects.all().count(), 3)

    def test_delete_from_s3(self):
        """
        delete_from_s3 should, well, delete from s3
        :return:
        """
        from portal.plugins.gnmatomresponder.models import ImportJob
        from portal.plugins.gnmatomresponder.tasks import delete_from_s3
        from django.conf import settings
        from datetime import datetime
        from boto.s3.bucket import Bucket

        mock_bucket = MagicMock(target=Bucket)
        mock_connection = MagicMock()
        mock_connection.get_bucket = MagicMock(return_value=mock_bucket)

        testjob = ImportJob(item_id="VX-123",job_id="VX-456", status="FINISHED",started_at=datetime.now(), s3_path="/path/to/s3/file")
        testjob.save = MagicMock()

        delete_from_s3(mock_connection, testjob)
        mock_connection.get_bucket.assert_called_once_with(settings.ATOM_RESPONDER_DOWNLOAD_BUCKET)
        mock_bucket.delete_key.assert_called_once_with("/path/to/s3/file")
        testjob.save.assert_called_once()