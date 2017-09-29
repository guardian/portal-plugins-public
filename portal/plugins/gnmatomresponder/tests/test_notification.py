from __future__ import absolute_import
import django.test
from mock import MagicMock, patch
import os
from django.core.management import execute_from_command_line

execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
execute_from_command_line(['manage.py', 'migrate', '--noinput'])
execute_from_command_line(['manage.py', 'loaddata', 'fixtures/ImportJobs.yaml'])


class TestNotification(django.test.TestCase):
    fixtures = [
        'ImportJobs'
    ]

    @staticmethod
    def _get_test_data(filename):
        mypath = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(mypath, "data", filename)) as f:
            return f.read()

    def test_process_notification(self):
        """
        process_notification should update the database with the status of the job that came back
        :return:
        """
        from portal.plugins.gnmatomresponder.notification import process_notification
        from portal.plugins.gnmatomresponder.job_notification import JobNotification
        from portal.plugins.gnmatomresponder.models import ImportJob
        from gnmvidispine.vs_item import VSItem
        mock_vsitem = MagicMock(target=VSItem)
        mock_vsitem.transcode = MagicMock(return_value="VX-888")

        with patch("gnmvidispine.vs_item.VSItem", return_value=mock_vsitem) as VSItemFactory:
            data = JobNotification(self._get_test_data("sample_notification.xml"))
            before_record = ImportJob.objects.get(job_id=data.jobId)
            self.assertEqual(before_record.status,'STARTED')
            process_notification(data)
            mock_vsitem.transcode.assert_called_once_with("lowres", allow_object=False, wait=False)
            after_record = ImportJob.objects.get(job_id=data.jobId)
            self.assertEqual(after_record.status,'FINISHED_WARNING')
