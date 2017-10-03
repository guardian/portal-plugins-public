import unittest
from mock import MagicMock, patch


class TestSentry(unittest.TestCase):
    def test_inform_sentry_exception(self):
        import raven
        from portal.plugins.kinesisresponder.sentry import inform_sentry_exception

        mock_client = MagicMock(target=raven.Client)
        with patch('raven.Client', return_value=mock_client):
            inform_sentry_exception(extra_ctx={'key': 'value'})

            mock_client.extra_context.assert_called_once_with({'key': 'value'})
            mock_client.captureException.assert_called_once_with()

    def test_inform_sentry(self):
        import raven
        from portal.plugins.kinesisresponder.sentry import inform_sentry

        mock_client = MagicMock(target=raven.Client)
        with patch('raven.Client', return_value=mock_client):
            inform_sentry("something happened", extra_ctx={'key': 'value'})

            mock_client.extra_context.assert_called_once_with({'key': 'value'})
            mock_client.captureMessage.assert_called_once_with("something happened")
