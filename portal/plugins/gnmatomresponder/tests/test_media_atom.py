import django.test
from mock import patch
from datetime import datetime


class TestMediaAtomToken(django.test.TestCase):
    maxDiff = None

    def test_get_token(self):
        """
        get_token should generate a one-time token for server->server communication
        :return:
        """
        from portal.plugins.gnmatomresponder.media_atom import get_token
        result = get_token("https://my-server/my-path","SomeKindaLongSecret", override_time=datetime(2018,03,01,12,13,14))
        print result
        self.assertEqual(result, ('HMAC CmHxn3zNXARg4zq/e81+mcqpyY2i1+AjYCoVM/NjihM=', 'Thu, 01 Mar 2018 18:13:14 GMT'))


class MockResponse(object):
    def __init__(self, status_code, body, headers):
        self.status_code = status_code
        self.text = body
        self.headers = headers

    def json(self):
        import json
        return json.loads(self.text)


class TestMediaAtomResend(django.test.TestCase):
    def test_atom_resend_normal(self):
        """
        request_atom_resend should send a resend request to the atom tool
        :return:
        """
        with patch("portal.plugins.gnmatomresponder.media_atom.get_token", return_value=('HMAC fake-code', 'Thu, 01 Mar 2018 18:13:14 GMT')) as mock_get_token:
            with patch("requests.post", return_value=MockResponse(200, """{"status":"ok"}""", {"Content-Type":"application/json"})) as mock_post:
                from portal.plugins.gnmatomresponder.media_atom import request_atom_resend, HttpError

                request_atom_resend("fake-atomid","myhost","SomeSillySecret")

                mock_get_token.assert_called_once_with("https://myhost/api/pluto/resend/fake-atomid", "SomeSillySecret")
                mock_post.assert_called_once_with('https://myhost/api/pluto/resend/fake-atomid', headers={'X-Gu-Tools-HMAC-Date': 'Thu, 01 Mar 2018 18:13:14 GMT', 'X-Gu-Tools-HMAC-Token': 'HMAC fake-code'})

    def test_atom_resend_error(self):
        """
        request_atom_resend should raise an exception if an error occurs
        :return:
        """
        with patch("portal.plugins.gnmatomresponder.media_atom.get_token", return_value=('HMAC fake-code', 'Thu, 01 Mar 2018 18:13:14 GMT')) as mock_get_token:
            with patch("requests.post", return_value=MockResponse(500, """{"status":"error"}""", {"Content-Type":"application/json"})) as mock_post:
                from portal.plugins.gnmatomresponder.media_atom import request_atom_resend, HttpError
                with self.assertRaises(HttpError) as raised_excep:
                    request_atom_resend("fake-atomid","myhost","SomeSillySecret")

                mock_get_token.assert_called_once_with("https://myhost/api/pluto/resend/fake-atomid", "SomeSillySecret")
                mock_post.assert_called_once_with('https://myhost/api/pluto/resend/fake-atomid', headers={'X-Gu-Tools-HMAC-Date': 'Thu, 01 Mar 2018 18:13:14 GMT', 'X-Gu-Tools-HMAC-Token': 'HMAC fake-code'})
                self.assertEqual(raised_excep.exception.code, 500)
                self.assertEqual(raised_excep.exception.uri, "https://myhost/api/pluto/resend/fake-atomid")
                self.assertEqual(raised_excep.exception.request_headers, {'X-Gu-Tools-HMAC-Date': 'Thu, 01 Mar 2018 18:13:14 GMT', 'X-Gu-Tools-HMAC-Token': 'HMAC fake-code'})
                self.assertEqual(raised_excep.exception.response_headers, {"Content-Type":"application/json"})