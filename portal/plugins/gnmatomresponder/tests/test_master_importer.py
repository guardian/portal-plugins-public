# -*- coding: utf-8 -*-
import django.test
from mock import MagicMock, patch
from gnmvidispine.vs_collection import VSCollection
from django.core.management import execute_from_command_line

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
            'projectId': "VX-567",
            'title': u"Søméthîng wîth ëxtënded çharacters – like this. £"
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

                m.import_new_item(master_item, fake_data, parent=project_collection)
                pac_processor.link_to_item.assert_called_once_with(pacxml, master_item)
                project_collection.addToCollection.assert_called_once_with(master_item)
                master_item.import_to_shape.assert_called_once_with(essence=True, jobMetadata={'gnm_source': 'media_atom'}, priority='HIGH', shape_tag='lowres', uri='file:///path/to/local/file')

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

                m.import_new_item(master_item, fake_data, parent=project_collection)
                pac_processor.link_to_item.assert_not_called()
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

    def test_pac_message(self):
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        from portal.plugins.gnmatomresponder.pac_xml import PacXmlProcessor
        from portal.plugins.gnmatomresponder.models import PacFormXml
        import json

        message = {u's3Bucket': u'media-atom-maker-upload-prod', u's3Path': u'uploads/0428f4ce-9f1f-4ad6-84d7-e4118936cae1-1/pac.xml', u'atomId': u'57AF5F3B-A556-448B-98E1-0628FDE9A5AC', u'type': u'pac-file-upload'}
        json_msg = json.dumps(message)

        pac_processor = MagicMock(target=PacXmlProcessor)
        pac_processor.link_to_item = MagicMock()

        pacxml = PacFormXml.objects.get(atom_id=message['atomId'])

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials'):
            with patch('portal.plugins.gnmatomresponder.pac_xml.PacXmlProcessor', return_value=pac_processor):
                m = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")
                m.ingest_pac_xml = MagicMock()
                m.import_new_item = MagicMock()

                m.process(json_msg,None)
                m.import_new_item.assert_not_called()
                m.ingest_pac_xml.assert_called_once_with(pacxml)

    def test_assign_atom_to_project(self):
        """
        assign_atom_to_project should do an assignment
        :return:
        """
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        import portal.plugins.gnmatomresponder.constants as const
        from gnmvidispine.vs_item import VSItem

        mock_item = MagicMock(target=VSItem)
        mock_item.get = MagicMock(return_value=None)

        mock_collection = MagicMock(target=VSCollection)
        mock_collection.get = MagicMock(return_value="VX-123")
        mock_collection.addToCollection = MagicMock()

        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials'):
            m = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")

            m.get_item_for_atomid = MagicMock(return_value=mock_item)
            m.get_collection_for_id = MagicMock(return_value=mock_collection)
            m.set_project_fields_for_master = MagicMock(return_value=mock_item)

            m.assign_atom_to_project("D64EEBD7-6033-4DC6-A0CA-1BBFA5A6DD95","VX-123","VX-456",mock_item)
            mock_item.get.assert_called_once_with(const.PARENT_COLLECTION)
            mock_collection.get.assert_called_once_with(const.PARENT_COLLECTION)
            mock_collection.addToCollection.assert_called_once_with(mock_item)
            m.set_project_fields_for_master.assert_called_once_with(mock_item, parent_project=mock_collection)

    def test_reassign_atom_to_project(self):
        """
        assign_atom_to_project should remove the given master from a project that it's already attached to
        :return:
        """
        from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
        import portal.plugins.gnmatomresponder.constants as const
        from gnmvidispine.vs_item import VSItem

        mock_item = MagicMock(target=VSItem)
        mock_item.get = MagicMock(return_value="VX-444")

        mock_old_collection = MagicMock(target=VSCollection)

        mock_collection = MagicMock(target=VSCollection)
        mock_collection.get = MagicMock(return_value="VX-123")
        mock_collection.addToCollection = MagicMock()


        with patch('portal.plugins.gnmatomresponder.master_importer.MasterImportResponder.refresh_access_credentials'):
            m = MasterImportResponder("fake role", "fake session", "fake stream", "shard-00000")

            m.get_item_for_atomid = MagicMock(return_value=mock_item)
            m.get_collection_for_id = MagicMock(side_effect=[mock_old_collection, mock_collection])
            m.set_project_fields_for_master = MagicMock(return_value=mock_item)

            m.assign_atom_to_project("D64EEBD7-6033-4DC6-A0CA-1BBFA5A6DD95","VX-123","VX-456",mock_item)
            mock_item.get.assert_called_once_with(const.PARENT_COLLECTION)
            mock_old_collection.removeFromCollection.assert_called_once_with(mock_item)
            mock_collection.get.assert_called_once_with(const.PARENT_COLLECTION)
            mock_collection.addToCollection.assert_called_once_with(mock_item)
            m.set_project_fields_for_master.assert_called_once_with(mock_item, parent_project=mock_collection)