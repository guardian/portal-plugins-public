import django.test
from mock import MagicMock,patch
import re


class TestS3Mixin(django.test.TestCase):
    class MockS3Conn(object):
        def __init__(self, fake_key, expected_keyname=None,expected_bucketname=None):
            self.fake_key = fake_key
            self.expected_bucketname = expected_bucketname
            self.expected_keyname = expected_keyname

        class MockBucket(object):
            def __init__(self, parent, name, expected_keyname=None):
                self.bucketname = name
                self.parent = parent
                self.expected_keyname = expected_keyname

            def get_key(self, keyname):
                if self.expected_keyname is not None and self.expected_keyname!=keyname:
                    raise AssertionError("Expected key name '{0}', got '{1}'".format(self.expected_keyname, keyname))
                return self.parent.fake_key

        def get_bucket(self, bucketname):
            if self.expected_bucketname is not None and self.expected_bucketname!=bucketname:
                raise AssertionError("Expected bucket name '{0}', got '{1}'".format(self.expected_bucketname, bucketname))
            return self.MockBucket(self,bucketname, expected_keyname=self.expected_keyname)

    def test_get_s3_signed_url(self):
        import boto.s3.key
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        fake_key = MagicMock(target=boto.s3.key.Key)
        fake_key.generate_url = MagicMock(return_value="https://some/invalid/url")
        mock_conn = self.MockS3Conn(fake_key,expected_bucketname="bucketname", expected_keyname="keyname")

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.get_s3_connection', return_value = mock_conn):
                r = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                mock_refresh_creds.assert_called_once()
                result = r.get_s3_signed_url("bucketname","keyname")
                fake_key.generate_url.assert_called_once_with(3600,query_auth=True)
                self.assertEqual(result, "https://some/invalid/url")

    def test_get_download_filename(self):
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder

        result = MasterImportResponder.get_download_filename("some/path/to/filename.xxx")
        self.assertEqual(result, "/path/to/download/filename.xxx")

        result_with_spaces = MasterImportResponder.get_download_filename("some/path/to filename   with spaces and #^3!")
        self.assertEqual(result_with_spaces, "/path/to/download/to_filename_with_spaces_and_3_")

    def test_get_download_filename_override(self):
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder

        result = MasterImportResponder.get_download_filename("some/path/to/filename.xxx", overridden_name="my overriden file.mp4")
        self.assertEqual(result, "/path/to/download/my_overriden_file.mp4")

    def test_get_download_filename_dedupe(self):
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder

        def mock_exists(path):
            """
            fake the os.path.exists to pretend files do exist, up to a given number
            :param path:
            :return:
            """
            number_part = re.search(r'-(\d+).[^\.]+$', path)
            if number_part:
                number = int(number_part.group(1))
                if number<3: return True
                return False
            else:
                return True

        with patch("os.path.exists", mock_exists):
            result = MasterImportResponder.get_download_filename("unrelated/path/for/a/filename.xxx")
            self.assertEqual("/path/to/download/filename-3.xxx", result)