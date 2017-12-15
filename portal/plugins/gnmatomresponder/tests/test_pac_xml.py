import django.test
from mock import MagicMock, patch
from django.core.management import execute_from_command_line
import django_test_settings
import os.path

if os.path.exists(django_test_settings.DATABASES['default']['NAME']):
    os.unlink(django_test_settings.DATABASES['default']['NAME'])

execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
execute_from_command_line(['manage.py', 'migrate', '--noinput'])
execute_from_command_line(['manage.py', 'loaddata', 'fixtures/PacFormXml.yaml'])
execute_from_command_line(['manage.py', 'loaddata', 'fixtures/Users.yaml'])

# Store original __import__
orig_import = __import__

### Patch up imports for Portal-specific stuff that is not accessible in CircleCI
edl_import_mock = MagicMock()

def import_mock(name, *args, **kwargs):
    if name == 'portal.plugins.gnm_masters.edl_import':
        return edl_import_mock

    return orig_import(name, *args, **kwargs)


class TestPacXmlProcessor(django.test.TestCase):
    fixtures = [
        "PacFormXml",
        "Users"
    ]

    def test_link_to_item(self):
        from portal.plugins.gnmatomresponder.pac_xml import PacXmlProcessor
        from portal.plugins.gnmatomresponder.models import PacFormXml
        from django.contrib.auth.models import User
        from gnmvidispine.vs_item import VSItem

        pacdata = PacFormXml.objects.get(atom_id='57AF5F3B-A556-448B-98E1-0628FDE9A5AC')
        master_item = MagicMock(target=VSItem)
        user = User.objects.get(username='admin')

        with patch('__builtin__.__import__', side_effect=import_mock):
            with patch('__builtin__.open', create=True) as mock_open:
                mock_open.return_value = MagicMock(spec=file)
                p = PacXmlProcessor("fake_role","fake_session")

                p.download_to_local_location = MagicMock(return_value="/path/to/local/datafile")

                p.link_to_item(pacdata, master_item)

                p.download_to_local_location.assert_called_once_with(bucket="bucketname",key="path/to/content.xml")
                file_handle = mock_open.return_value.__enter__.return_value
                edl_import_mock.update_edl_data.assert_called_once_with(file_handle, master_item.name, user)