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
        process_notification should update the database with the status of the job that came back,
        and should call handle_failed_job if there was an error
        :return:
        """
        from portal.plugins.gnmatomresponder.job_notification import JobNotification
        from portal.plugins.gnmatomresponder.models import ImportJob
        from gnmvidispine.vs_item import VSItem
        mock_vsitem = MagicMock(target=VSItem)
        mock_vsitem.transcode = MagicMock(return_value="VX-888")

        with patch("gnmvidispine.vs_item.VSItem", return_value=mock_vsitem) as VSItemFactory:
            with patch("portal.plugins.gnmatomresponder.notification.handle_failed_job") as mock_handle_failed_job:
                from portal.plugins.gnmatomresponder.notification import process_notification
                data = JobNotification(self._get_test_data("sample_notification.xml"))
                before_record = ImportJob.objects.get(job_id=data.jobId)
                self.assertEqual(before_record.status,'STARTED')
                process_notification(data)
                after_record = ImportJob.objects.get(job_id=data.jobId)
                self.assertEqual(after_record.status,'FINISHED_WARNING')
                mock_handle_failed_job.assert_called_once_with(before_record)

    def test_process_notification_worked(self):
        """
        process_notification should update the database with the status of the job that came back,
        and should NOT call handle_failed_job if there was no error
        :return:
        """
        from portal.plugins.gnmatomresponder.job_notification import JobNotification
        from portal.plugins.gnmatomresponder.models import ImportJob
        from gnmvidispine.vs_item import VSItem
        mock_vsitem = MagicMock(target=VSItem)
        mock_vsitem.transcode = MagicMock(return_value="VX-888")

        with patch("gnmvidispine.vs_item.VSItem", return_value=mock_vsitem) as VSItemFactory:
            with patch("portal.plugins.gnmatomresponder.notification.handle_failed_job") as mock_handle_failed_job:
                from portal.plugins.gnmatomresponder.notification import process_notification
                data = JobNotification(self._get_test_data("sample_notification_2.xml"))
                before_record = ImportJob.objects.get(job_id=data.jobId)
                self.assertEqual(before_record.status,'STARTED')
                process_notification(data)
                after_record = ImportJob.objects.get(job_id=data.jobId)
                self.assertEqual(after_record.status,'FINISHED')
                mock_handle_failed_job.assert_not_called()

    def test_handle_failed_job(self):
        """
        handle_failed_job should ask Celery to run the retry task after an exponential delay
        :return:
        """
        from portal.plugins.gnmatomresponder.models import ImportJob

        fakejob = ImportJob(
            item_id='VX-123',
            job_id='VX-456',
            atom_id='060386C2-3764-47F9-B338-F71E4E0704A7',
            retry_number=0
        )

        with patch("portal.plugins.gnmatomresponder.tasks.timed_request_resend.apply_async") as mock_send_request:
            from portal.plugins.gnmatomresponder.notification import handle_failed_job

            handle_failed_job(fakejob)
            mock_send_request.assert_called_once_with(args=('060386C2-3764-47F9-B338-F71E4E0704A7', ), countdown=4)
            mock_send_request.reset_mock()

            fakejob.retry_number=1
            handle_failed_job(fakejob)
            mock_send_request.assert_called_once_with(args=('060386C2-3764-47F9-B338-F71E4E0704A7', ), countdown=16)
            mock_send_request.reset_mock()

            fakejob.retry_number=2
            handle_failed_job(fakejob)
            mock_send_request.assert_called_once_with(args=('060386C2-3764-47F9-B338-F71E4E0704A7', ), countdown=64)
            mock_send_request.reset_mock()

            fakejob.retry_number=3
            handle_failed_job(fakejob)
            mock_send_request.assert_called_once_with(args=('060386C2-3764-47F9-B338-F71E4E0704A7', ), countdown=256)
            mock_send_request.reset_mock()