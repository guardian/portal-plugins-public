import django.test
from mock import MagicMock, patch

import logging
logging.basicConfig(level=logging.INFO)


class TestSignals(django.test.TestCase):
    fixtures = [
        "PacFormXml"
    ]

    def test_edl_import_success(self):
        """
        edl_import_success should update the database record when task completes successfully
        :return:
        """
        from portal.plugins.gnmatomresponder.signals import edl_import_success
        from portal.plugins.gnmatomresponder.models import PacFormXml
        from celery import Task

        mock_sender = MagicMock(target=Task)
        mock_sender.name = "test_task"

        mock_sender.request.id = "bbba3673-1f46-4a7f-a549-81bac11955e7"

        edl_import_success(sender=mock_sender)

        pacmodel = PacFormXml.objects.get(celery_task_id=mock_sender.request.id)
        self.assertEqual(pacmodel.status,"PROCESSED")
        self.assertEqual(pacmodel.last_error,"")

    def test_edl_import_failure(self):
        """
        edl_import_success should update the database record when task fails
        :return:
        """
        from portal.plugins.gnmatomresponder.signals import edl_import_failure
        from portal.plugins.gnmatomresponder.models import PacFormXml
        from celery import Task
        import traceback

        mock_error = MagicMock(target=RuntimeError)
        mock_trace = MagicMock(target=traceback)
        mock_trace.format_exc = MagicMock(return_value="simulated stack trace string")
        mock_sender = MagicMock(target=Task)
        mock_sender.name = "test_task"

        mock_sender.request.id = "bbba3673-1f46-4a7f-a549-81bac11955e7"

        edl_import_failure(task_id="bbba3673-1f46-4a7f-a549-81bac11955e7",exception=mock_error,traceback=mock_trace,sender=mock_sender)

        pacmodel = PacFormXml.objects.get(celery_task_id=mock_sender.request.id)
        self.assertEqual(pacmodel.status,"ERROR")
        self.assertEqual(pacmodel.last_error,"simulated stack trace string")

    def test_edl_import_revoked(self):
        """
        edl_import_success should update the database record when task completes successfully
        :return:
        """
        from portal.plugins.gnmatomresponder.signals import edl_import_revoked
        from portal.plugins.gnmatomresponder.models import PacFormXml
        from celery import Task

        mock_sender = MagicMock(target=Task)
        mock_sender.name = "test_task"

        mock_sender.request.id = "bbba3673-1f46-4a7f-a549-81bac11955e7"

        edl_import_revoked(sender=mock_sender,terminated=True,signum=15,expired=True)

        pacmodel = PacFormXml.objects.get(celery_task_id=mock_sender.request.id)
        self.assertEqual(pacmodel.status,"ERROR")
        self.assertEqual(pacmodel.last_error,"Task revoked on signal number 15\nTerminated? True\nExpired? True")