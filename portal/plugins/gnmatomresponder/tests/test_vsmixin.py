import django.test
from mock import MagicMock, patch
from gnmvidispine.vs_item import VSItem
from gnmvidispine.vs_collection import VSCollection
from gnmvidispine.vs_search import VSItemSearch


class TestVsMixin(django.test.TestCase):
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
            with patch('portal.plugins.gnmatomresponder.vs_mixin.VSItemSearch', return_value = mock_search):

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
            with patch('portal.plugins.gnmatomresponder.vs_mixin.VSItemSearch', return_value = mock_search):
                r = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                mock_refresh_creds.assert_called_once()

                result = r.get_item_for_atomid("f6ba9036-3f53-4850-9c75-fe3bcfbae4b2")
                mock_search.addCriterion.assert_called_once_with(
                    {'gnm_master_mediaatom_atomid': "f6ba9036-3f53-4850-9c75-fe3bcfbae4b2",
                     'gnm_type': 'Master'}
                )

                self.assertEqual(result, None)

    def test_get_item_for_atomid_multiple(self):
        """
        get_item_for_atomid should return the first item if multiple records match
        :return:
        """
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder

        mock_item = MagicMock(target=VSItem)
        mock_search = MagicMock(target=VSItemSearch)
        mock_search.addCriterion = MagicMock()
        mock_search.execute = MagicMock(return_value=self.MockSearchResult([mock_item, MagicMock(target=VSItem), MagicMock(target=VSItem)]))
        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            with patch('portal.plugins.gnmatomresponder.vs_mixin.VSItemSearch', return_value = mock_search):

                r = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                mock_refresh_creds.assert_called_once()

                result = r.get_item_for_atomid("f6ba9036-3f53-4850-9c75-fe3bcfbae4b2")
                mock_search.addCriterion.assert_called_once_with(
                    {'gnm_master_mediaatom_atomid': "f6ba9036-3f53-4850-9c75-fe3bcfbae4b2",
                     'gnm_type': 'Master'}
                )

                self.assertEqual(result, mock_item)

    def test_set_project_fields_for_master(self):
        """
        set_project_fields_for_master should retrieve metadata references for the given collection and set them
        as metadata on the given item
        :return:
        """
        from gnmvidispine.vs_metadata import VSMetadataAttribute,VSMetadataReference, VSMetadataValue
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        mock_item = MagicMock(target=VSItem)
        mock_item.createPlaceholder = MagicMock()
        mock_project = MagicMock(target=VSCollection)
        mock_project_name_attrib = MagicMock(target=VSMetadataAttribute)
        mock_project_name_attrib.uuid = "c4a7cd79-7652-47ba-bd3b-37492cdb91aa"
        mock_project_name_attrib.values = [VSMetadataValue(uuid="B9A8D873-F704-4BA0-A339-17BF456FEA7C")]
        mock_commission_name_attrib = MagicMock(target=VSMetadataAttribute)
        mock_commission_name_attrib.references = [VSMetadataReference(uuid="8CDFBE79-7F08-4D66-9048-0CC33F664937")]
        mock_commission_name_attrib.uuid = "41cce471-2b30-48fa-8af2-b0d42aff6c7f"

        mock_project.get_metadata_attributes = MagicMock(side_effect=[
            [mock_project_name_attrib],
            [mock_commission_name_attrib]
        ])

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            with patch('portal.plugins.gnmatomresponder.vs_mixin.VSItem', return_value=mock_item):
                r = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                mock_refresh_creds.assert_called_once()

                r.set_project_fields_for_master(mock_item,mock_project)
                mock_item.set_metadata.assert_called_once_with({
                    'gnm_commission_title': VSMetadataReference(uuid="41cce471-2b30-48fa-8af2-b0d42aff6c7f"),
                    'gnm_project_headline': VSMetadataReference(uuid="c4a7cd79-7652-47ba-bd3b-37492cdb91aa")
                }, group="Asset")

    def test_create_placeholder_for_atomid(self):
        """
        create_placeholder_for_atomid should create a placeholder with relevant metadata
        :return:
        """
        from gnmvidispine.vs_metadata import VSMetadataAttribute,VSMetadataReference, VSMetadataValue
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        mock_item = MagicMock(target=VSItem)
        mock_item.createPlaceholder = MagicMock()
        mock_project = MagicMock(target=VSCollection)
        mock_project_name_attrib = MagicMock(target=VSMetadataAttribute)
        mock_project_name_attrib.uuid = "c4a7cd79-7652-47ba-bd3b-37492cdb91aa"
        mock_project_name_attrib.values = [VSMetadataValue(uuid="B9A8D873-F704-4BA0-A339-17BF456FEA7C")]
        mock_commission_name_attrib = MagicMock(target=VSMetadataAttribute)
        mock_commission_name_attrib.references = [VSMetadataReference(uuid="8CDFBE79-7F08-4D66-9048-0CC33F664937")]
        mock_commission_name_attrib.uuid = "41cce471-2b30-48fa-8af2-b0d42aff6c7f"

        mock_project.get_metadata_attributes = MagicMock(side_effect=[
            [mock_project_name_attrib],
            [mock_commission_name_attrib]
        ])

        self.assertEqual(VSMetadataReference(uuid="B9A8D873-F704-4BA0-A339-17BF456FEA7C"),VSMetadataReference(uuid="B9A8D873-F704-4BA0-A339-17BF456FEA7C"))
        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            with patch('portal.plugins.gnmatomresponder.vs_mixin.VSItem', return_value=mock_item):
                r = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                mock_refresh_creds.assert_called_once()
                r.create_placeholder_for_atomid("f6ba9036-3f53-4850-9c75-fe3bcfbae4b2",
                                                title="fake title",
                                                user="joe.bloggs@mydomain.com",
                                                parent=mock_project)
                mock_item.createPlaceholder.assert_called_once_with(
                    {'title': 'fake title',
                     'gnm_commission_title': VSMetadataReference(uuid="41cce471-2b30-48fa-8af2-b0d42aff6c7f"),
                     'gnm_project_headline': VSMetadataReference(uuid="c4a7cd79-7652-47ba-bd3b-37492cdb91aa"),
                     'gnm_asset_category': 'Master',
                     'gnm_type': 'Master',
                     'gnm_master_website_headline': 'fake title',
                     'gnm_master_mediaatom_atomid': 'f6ba9036-3f53-4850-9c75-fe3bcfbae4b2',
                     'gnm_master_generic_titleid': 'f6ba9036-3f53-4850-9c75-fe3bcfbae4b2',
                     'gnm_master_mediaatom_uploaded_by': 'joe.bloggs@mydomain.com'
                     }, group='Asset'
                )

    def test_get_collection_for_projectid(self):
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder

        mock_collection = MagicMock(target=VSCollection)
        mock_collection.populate = MagicMock()
        mock_collection.get = MagicMock(return_value='Project')

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            with patch('portal.plugins.gnmatomresponder.vs_mixin.VSCollection', return_value=mock_collection):
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
            with patch('portal.plugins.gnmatomresponder.vs_mixin.VSCollection', return_value=mock_collection):
                r = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")

                with self.assertRaises(NotAProjectError) as excep:
                    result = r.get_collection_for_id("VX-234")
                mock_collection.populate.assert_called_once_with("VX-234")
                self.assertEqual(excep.exception.message,"VX-234 is a Gumby")
