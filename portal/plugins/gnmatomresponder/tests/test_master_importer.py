import django.test
from mock import MagicMock, patch
from gnmvidispine.vs_item import VSItem
from gnmvidispine.vs_search import VSItemSearch
from gnmvidispine.vs_collection import VSCollection

class TestMasterImporter(django.test.TestCase):
    class MockSearchResult(object):
        def __init__(self, results):
            self._results = results
            self.totalItems = len(results)

        def results(self,shouldPopulate=False):
            for item in self._results:
                yield item

    class MockSearchClass(object):
        def execute(self):
            pass

    def test_get_item_for_atomid(self):
        """
        get_item_for_atomid should make a search for the provided atom id
        :return:
        """
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder

        mock_item = MagicMock(target=VSItem)
        mock_search = MagicMock(target=VSItemSearch)
        mock_search.addCriterion = MagicMock()
        mock_search.execute = MagicMock(return_value=self.MockSearchResult([mock_item]))
        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            with patch('portal.plugins.gnmatomresponder.master_importer.VSItemSearch', return_value = mock_search):

                r = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                mock_refresh_creds.assert_called_once()

                result = r.get_item_for_atomid("f6ba9036-3f53-4850-9c75-fe3bcfbae4b2")
                mock_search.addCriterion.assert_called_once_with(
                    {'gnm_master_mediaatom_atomid': "f6ba9036-3f53-4850-9c75-fe3bcfbae4b2",
                    'gnm_type': 'Master'}
                )

                self.assertEqual(result, mock_item)

    def test_get_item_for_atomid_notfound(self):
        """
        get_item_for_atomid should return None if no item exists
        :return:
        """
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder

        mock_search = MagicMock(target=VSItemSearch)
        mock_search.addCriterion = MagicMock()
        mock_search.execute = MagicMock(return_value=self.MockSearchResult([]))
        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            with patch('portal.plugins.gnmatomresponder.master_importer.VSItemSearch', return_value = mock_search):
                r = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                mock_refresh_creds.assert_called_once()

                result = r.get_item_for_atomid("f6ba9036-3f53-4850-9c75-fe3bcfbae4b2")
                mock_search.addCriterion.assert_called_once_with(
                    {'gnm_master_mediaatom_atomid': "f6ba9036-3f53-4850-9c75-fe3bcfbae4b2",
                     'gnm_type': 'Master'}
                )

                self.assertEqual(result, None)

    def test_create_placeholder_for_atomid(self):
        """
        create_placeholder_for_atomid should create a placeholder with relevant metadata
        :return:
        """
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        mock_item = MagicMock(target=VSItem)
        mock_item.createPlaceholder = MagicMock()

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            with patch('portal.plugins.gnmatomresponder.master_importer.VSItem', return_value=mock_item):
                r = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                mock_refresh_creds.assert_called_once()
                r.create_placeholder_for_atomid("f6ba9036-3f53-4850-9c75-fe3bcfbae4b2", title="fake title")
                mock_item.createPlaceholder.assert_called_once_with(
                    {
                        'gnm_type': 'Master',
                        'title': "fake title",
                        'gnm_master_website_headline': "fake title",
                        'gnm_master_mediaatom_atomid': "f6ba9036-3f53-4850-9c75-fe3bcfbae4b2",
                    },
                    group="Asset"
                )

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

    def test_get_collection_for_projectid(self):
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder

        mock_collection = MagicMock(target=VSCollection)
        mock_collection.populate = MagicMock()
        mock_collection.get = MagicMock(return_value='Project')

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            with patch('portal.plugins.gnmatomresponder.master_importer.VSCollection', return_value=mock_collection):
                r = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")

                result = r.get_collection_for_id("VX-234")
                mock_collection.populate.assert_called_once_with("VX-234")
                self.assertEqual(result, mock_collection)

    def test_get_collection_for_projectid_invalid(self):
        """
        get_collection_for_projectid should raise an exception if the returned collection is not a project
        :return:
        """
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        from portal.plugins.gnmatomresponder.exceptions import NotAProjectError

        mock_collection = MagicMock(target=VSCollection)
        mock_collection.populate = MagicMock()
        mock_collection.get = MagicMock(return_value='Gumby')

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            with patch('portal.plugins.gnmatomresponder.master_importer.VSCollection', return_value=mock_collection):
                r = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")

                with self.assertRaises(NotAProjectError) as excep:
                    result = r.get_collection_for_id("VX-234")
                mock_collection.populate.assert_called_once_with("VX-234")
                self.assertEqual(excep.exception.message,"VX-234 is a Gumby")

