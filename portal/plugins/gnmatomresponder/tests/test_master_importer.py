import django.test
from mock import MagicMock, patch
from gnmvidispine.vs_item import VSItem
from gnmvidispine.vs_search import VSItemSearch
from gnmvidispine.vs_collection import VSCollection
from django.core.management import execute_from_command_line
import re

execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
execute_from_command_line(['manage.py', 'migrate', '--noinput'])
execute_from_command_line(['manage.py', 'loaddata', 'fixtures/PacFormXml.yaml'])


class TestMasterImporter(django.test.TestCase):
    fixtures = [
        "PacFormXml"
    ]

    def test_register_pac_xml(self):
        """
        register_pac_xml should create a new data model entry
        :return:
        """
        from portal.plugins.gnmatomresponder.models import PacFormXml
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            m = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")

            fake_data = {
                'atomId': "5C6F1DC4-54E4-47DC-A582-C2470FEF88C2",
                's3Bucket': "bucketname",
                's3Path': "more/fun/data.xml"
            }

            #this record should not exist when we start
            with self.assertRaises(PacFormXml.DoesNotExist):
                PacFormXml.objects.get(atom_id=fake_data['atomId'])

            m.register_pac_xml(fake_data)

            result = PacFormXml.objects.get(atom_id=fake_data['atomId'])
            self.assertEqual(result.pacdata_url,"s3://bucketname/more/fun/data.xml")

    def test_register_pac_xml_existing(self):
        """
        register_pac_xml should return the id for an already existing id
        :return:
        """
        from portal.plugins.gnmatomresponder.models import PacFormXml
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            with patch('portal.plugins.gnmatomresponder.master_importer.logger.info') as mock_logger_info:
                m = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")

                fake_data = {
                    'atomId': "57AF5F3B-A556-448B-98E1-0628FDE9A5AC",
                    's3Bucket': "bucketname",
                    's3Path': "more/fun/data.xml"
                }

                m.register_pac_xml(fake_data)

                result = PacFormXml.objects.get(atom_id=fake_data['atomId'])
                self.assertEqual(result.pacdata_url,"s3://bucketname/more/fun/data.xml")
                #info message should be output
                mock_logger_info.assert_called_once()

    def test_import_new_item(self):
        """
        import_new_item should start ingest of an item and pick up the associated PAC form data
        :return:
        """
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        from portal.plugins.gnmatomresponder.pac_xml import PacXmlProcessor
        from portal.plugins.gnmatomresponder.models import PacFormXml

        from gnmvidispine.vs_item import VSItem
        fake_data = {
            'atomId': "57AF5F3B-A556-448B-98E1-0628FDE9A5AC",
            's3Key': "path/to/s3data",
            's3Bucket': "sandcastles",
            'projectId': "VX-567"
        }

        master_item = MagicMock(target=VSItem)
        master_item.import_to_shape=MagicMock()

        pac_processor = MagicMock(target=PacXmlProcessor)
        pac_processor.link_to_item = MagicMock()

        pacxml = PacFormXml.objects.get(atom_id=fake_data['atomId'])

        project_collection = MagicMock(target=VSCollection)
        project_collection.addToCollection = MagicMock()

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials'):
            with patch('portal.plugins.gnmatomresponder.pac_xml.PacXmlProcessor', return_value=pac_processor):
                m = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                m.download_to_local_location = MagicMock(return_value="/path/to/local/file")
                m.get_collection_for_id = MagicMock(return_value=project_collection)

                m.import_new_item(master_item, fake_data)
                pac_processor.link_to_item.assert_called_once_with(pacxml, master_item)
                m.get_collection_for_id.assert_called_once_with(fake_data['projectId'])
                project_collection.addToCollection.assert_called_once_with(master_item)
                master_item.import_to_shape.assert_called_once_with(essence=True, jobMetadata={'gnm_source': 'media_atom'}, priority='HIGH', shape_tag='lowres', uri='file:///path/to/local/file')

    def test_create_placeholder_for_atomid(self):
        """
        import_new_item should start ingest of an item and pick up the associated PAC form data
        :return:
        """
        from gnmvidispine.vs_metadata import VSMetadataAttribute,VSMetadataReference, VSMetadataValue
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        mock_item = MagicMock(target=VSItem)
        mock_item.createPlaceholder = MagicMock()
        mock_project = MagicMock(target=VSCollection)
        mock_project_name_attrib = MagicMock(target=VSMetadataAttribute)
        mock_project_name_attrib.values = [VSMetadataValue(uuid="B9A8D873-F704-4BA0-A339-17BF456FEA7C")]
        mock_commission_name_attrib = MagicMock(target=VSMetadataAttribute)
        mock_commission_name_attrib.references = [VSMetadataReference(uuid="8CDFBE79-7F08-4D66-9048-0CC33F664937")]

        mock_project.get_metadata_attributes = MagicMock(side_effect=[
            [mock_project_name_attrib],
            [mock_commission_name_attrib]
        ])

        self.assertEqual(VSMetadataReference(uuid="B9A8D873-F704-4BA0-A339-17BF456FEA7C"),VSMetadataReference(uuid="B9A8D873-F704-4BA0-A339-17BF456FEA7C"))
        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials') as mock_refresh_creds:
            with patch('portal.plugins.gnmatomresponder.master_importer.VSItem', return_value=mock_item):
                r = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                mock_refresh_creds.assert_called_once()
                r.create_placeholder_for_atomid("f6ba9036-3f53-4850-9c75-fe3bcfbae4b2",
                                                title="fake title",
                                                user="joe.bloggs@mydomain.com",
                                                parent=mock_project)
                mock_item.createPlaceholder.assert_called_once_with(
                    {'title': 'fake title',
                     'gnm_commission_title': [VSMetadataReference(uuid="8CDFBE79-7F08-4D66-9048-0CC33F664937")],
                     'gnm_project_headline': [VSMetadataReference(uuid="B9A8D873-F704-4BA0-A339-17BF456FEA7C")],
                     'gnm_asset_category': 'Master',
                     'gnm_type': 'Master',
                     'gnm_master_website_headline': 'fake title',
                     'gnm_master_mediaatom_atomid': 'f6ba9036-3f53-4850-9c75-fe3bcfbae4b2',
                     'gnm_master_generic_titleid': 'f6ba9036-3f53-4850-9c75-fe3bcfbae4b2',
                     'gnm_master_mediaatom_uploaded_by': 'joe.bloggs@mydomain.com'
                     }, group='Asset'
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

    def test_import_new_item_nopac(self):
        """
        import_new_item should start ingest of an item even when there is no pac data
        :return:
        """
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        from portal.plugins.gnmatomresponder.pac_xml import PacXmlProcessor
        from portal.plugins.gnmatomresponder.models import PacFormXml

        from gnmvidispine.vs_item import VSItem
        fake_data = {
            'atomId': "F6ED398D-9C71-4DBE-A519-C90F901CEB2A",
            's3Key': "path/to/s3data",
            's3Bucket': "sandcastles",
            'projectId': "VX-567"
        }

        master_item = MagicMock(target=VSItem)
        master_item.import_to_shape=MagicMock()

        pac_processor = MagicMock(target=PacXmlProcessor)
        pac_processor.link_to_item = MagicMock()

        #ensure that the atom id does not exist in our fixtures
        with self.assertRaises(PacFormXml.DoesNotExist):
            PacFormXml.objects.get(atom_id=fake_data['atomId'])

        project_collection = MagicMock(target=VSCollection)
        project_collection.addToCollection = MagicMock()

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials'):
            with patch('portal.plugins.gnmatomresponder.pac_xml.PacXmlProcessor', return_value=pac_processor):
                m = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                m.download_to_local_location = MagicMock(return_value="/path/to/local/file")
                m.get_collection_for_id = MagicMock(return_value=project_collection)

                m.import_new_item(master_item, fake_data)
                pac_processor.link_to_item.assert_not_called()
                m.get_collection_for_id.assert_called_once_with(fake_data['projectId'])
                project_collection.addToCollection.assert_called_once_with(master_item)
                master_item.import_to_shape.assert_called_once_with(essence=True, jobMetadata={'gnm_source': 'media_atom'}, priority='HIGH', shape_tag='lowres', uri='file:///path/to/local/file')

    def test_ingest_pac_xml(self):
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        from portal.plugins.gnmatomresponder.pac_xml import PacXmlProcessor
        from portal.plugins.gnmatomresponder.models import PacFormXml

        from gnmvidispine.vs_item import VSItem
        fake_data = {
            'atomId': "57AF5F3B-A556-448B-98E1-0628FDE9A5AC",
            's3Key': "path/to/s3data",
            's3Bucket': "sandcastles",
            'projectId': "VX-567"
        }

        master_item = MagicMock(target=VSItem)
        master_item.import_to_shape=MagicMock()

        pac_processor = MagicMock(target=PacXmlProcessor)
        pac_processor.link_to_item = MagicMock()

        pacxml = PacFormXml.objects.get(atom_id=fake_data['atomId'])

        project_collection = MagicMock(target=VSCollection)
        project_collection.addToCollection = MagicMock()

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials'):
            with patch('portal.plugins.gnmatomresponder.pac_xml.PacXmlProcessor', return_value=pac_processor):
                m = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                m.download_to_local_location = MagicMock(return_value="/path/to/local/file")
                m.get_collection_for_id = MagicMock(return_value=project_collection)
                m.get_item_for_atomid = MagicMock(return_value=master_item)

                m.ingest_pac_xml(pacxml)
                pac_processor.link_to_item.assert_called_once_with(pacxml, master_item)

    def test_ingest_pac_xml_notfound(self):
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        from portal.plugins.gnmatomresponder.pac_xml import PacXmlProcessor
        from portal.plugins.gnmatomresponder.models import PacFormXml

        fake_data = {
            'atomId': "57AF5F3B-A556-448B-98E1-0628FDE9A5AC",
            's3Key': "path/to/s3data",
            's3Bucket': "sandcastles",
            'projectId': "VX-567"
        }

        pac_processor = MagicMock(target=PacXmlProcessor)
        pac_processor.link_to_item = MagicMock()

        pacxml = PacFormXml.objects.get(atom_id=fake_data['atomId'])

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials'):
            with patch('portal.plugins.gnmatomresponder.pac_xml.PacXmlProcessor', return_value=pac_processor):
                m = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                m.get_item_for_atomid = MagicMock(return_value=None)

                m.ingest_pac_xml(pacxml)
                pac_processor.link_to_item.assert_not_called()