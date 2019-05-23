from __future__ import absolute_import
from mock import MagicMock, patch
import django.test


class TestGetShapeFor(django.test.TestCase):
    def test_get_shape_for_valid(self):
        """
        get_shape_for should return a shape if it exists and not request a transcode
        :return:
        """
        from gnmvidispine.vs_item import VSItem
        from gnmvidispine.vs_shape import VSShape
        from portal.plugins.gnmdownloadablelink.tasks import get_shape_for

        mock_item = MagicMock(target=VSItem)
        mock_shape = MagicMock(target=VSShape)
        mock_item.transcode = MagicMock()
        mock_item.get_shape = MagicMock(return_value=mock_shape)

        result = get_shape_for(mock_item,"original")
        self.assertEqual(result, mock_shape)
        mock_item.transcode.assert_not_called()

    def test_get_shape_for_notexist(self):
        """
        get_shape_for should request a shape transcode if no shape could be found
        :return:
        """
        from gnmvidispine.vs_item import VSItem,VSNotFound
        from portal.plugins.gnmdownloadablelink.tasks import get_shape_for, TranscodeRequested

        mock_item = MagicMock(target=VSItem)
        mock_item.transcode = MagicMock()
        mock_item.get_shape = MagicMock(side_effect=VSNotFound)

        with self.assertRaises(TranscodeRequested):
            result = get_shape_for(mock_item,"mezzanine")
        mock_item.transcode.assert_called_once_with('mezzanine', allow_object=False, priority='MEDIUM', wait=False)

    def test_get_shape_for_vserror(self):
        """
        get_shape_for should pass through other vidispine errors
        :return:
        """
        from gnmvidispine.vs_item import VSItem,VSNotFound, VSBadRequest
        from gnmvidispine.vs_shape import VSShape
        from portal.plugins.gnmdownloadablelink.tasks import get_shape_for, TranscodeRequested

        mock_item = MagicMock(target=VSItem)
        mock_item.transcode = MagicMock()
        mock_item.get_shape = MagicMock(side_effect=VSBadRequest)

        with self.assertRaises(VSBadRequest):
            result = get_shape_for(mock_item,"mezzanine")
        mock_item.transcode.assert_not_called()


class TestCreateLinkFor(django.test.TestCase):
    fixtures = [
        "links"
    ]

    def test_create_link_for_valid(self):
        """
        if a shape is existing, create_link_for should immediately upload and create a link
        :return:
        """
        from gnmvidispine.vs_shape import VSShape
        from gnmvidispine.vs_item import VSItem
        from portal.plugins.gnmdownloadablelink.models import DownloadableLink

        mock_item = MagicMock(target=VSItem)
        mock_item.populate = MagicMock()
        mock_item.get = MagicMock(return_value="item title here")
        mock_shape = MagicMock(target=VSShape)

        mock_s3key = MagicMock()
        mock_s3key.bucket_name="test_bucket"
        mock_s3key.key="path/to/uploaded_file"

        mock_s3client = MagicMock()
        mock_s3client.generate_presigned_url = MagicMock(return_value="https://fake-download-url")

        mdl_before = DownloadableLink.objects.get(item_id="VX-11", shapetag="original")
        self.assertEqual(mdl_before.status, "Requested")

        with patch("gnmvidispine.vs_item.VSItem", return_value=mock_item):
            with patch("portal.plugins.gnmdownloadablelink.tasks.get_shape_for", return_value=mock_shape) as mock_get_shape:
                with patch("portal.plugins.gnmdownloadablelink.tasks.upload_to_s3", return_value=mock_s3key) as mock_upload:
                    with patch("portal.plugins.gnmdownloadablelink.tasks.create_link_for.apply_async") as mock_apply:
                        with patch("portal.plugins.gnmdownloadablelink.tasks.s3_connect_lowerlevel", return_value=mock_s3client):
                            from portal.plugins.gnmdownloadablelink.tasks import create_link_for
                            result = create_link_for("VX-11", "original", obfuscate=False)

                            mock_get_shape.assert_called_once_with(mock_item,"original",allow_transcode=True)
                            mock_item.populate.assert_called_once_with('VX-11', specificFields=['title'])
                            mock_upload.assert_called_once_with(mock_shape, filename="item_title_here")
                            mock_s3client.generate_presigned_url.assert_called_once()
                            mock_apply.assert_not_called()
                            mdl_after = DownloadableLink.objects.get(item_id="VX-11", shapetag="original")
                            self.assertEqual(mdl_after.status, "Available")
                            self.assertEqual(mdl_after.public_url, 'https://fake-download-url')
                            self.assertEqual(mdl_after.s3_url, "s3://fake_bucket/path/to/uploaded_file")

    def test_create_link_for_noshape(self):
        """
        if a shape is not existing, create_link_for should request a transcode and exit
        :return:
        """
        from portal.plugins.gnmdownloadablelink.tasks import TranscodeRequested, NeedsRetry
        from portal.plugins.gnmdownloadablelink.models import DownloadableLink
        from boto.s3.key import Key
        from gnmvidispine.vs_shape import VSShape
        from gnmvidispine.vs_item import VSItem

        mock_item = MagicMock(target=VSItem)
        mock_item.populate = MagicMock()
        mock_item.get = MagicMock(return_value="item title here")
        mock_shape = MagicMock(target=VSShape)

        mock_s3key = MagicMock(target=Key)
        mock_s3key.set_canned_acl = MagicMock()
        mock_s3key.generate_url = MagicMock(return_value="https://fake-download-url")
        mock_s3key.key = "path/to/uploaded_file"

        mdl_before = DownloadableLink.objects.get(item_id="VX-11", shapetag="mezzanine")
        self.assertEqual(mdl_before.status, "Available")

        with patch("gnmvidispine.vs_item.VSItem", return_value=mock_item):
            with patch("portal.plugins.gnmdownloadablelink.tasks.get_shape_for", side_effect=TranscodeRequested("VX-11")) as mock_get_shape:
                with patch("portal.plugins.gnmdownloadablelink.tasks.upload_to_s3") as mock_upload:
                    with patch("portal.plugins.gnmdownloadablelink.tasks.create_link_for.apply_async") as mock_apply:
                        from portal.plugins.gnmdownloadablelink.tasks import create_link_for
                        result = create_link_for("VX-11", "mezzanine", obfuscate=False)

                        mock_get_shape.assert_called_once_with(mock_item,"mezzanine",allow_transcode=True)
                        mock_item.populate.assert_called_once_with('VX-11', specificFields=['title'])
                        mock_upload.assert_not_called()
                        mock_s3key.generate_url.assert_not_called()
                        mock_apply.assert_called_once_with(('VX-11', 'mezzanine'), countdown=30, kwargs={'obfuscate': False, 'is_update': True})

                        mdl_after = DownloadableLink.objects.get(item_id="VX-11", shapetag="mezzanine")
                        self.assertEqual(mdl_after.status, "Transcoding")
                        self.assertEqual(mdl_after.public_url, 'http://s3.someregion.amazonaws.com/bucket_name/somethingsomethingsomething')
                        self.assertEqual(mdl_after.s3_url, 's3://bucket_name/path/to/file.ext')

    def test_create_link_for_needsretry(self):
        """
        if a transcode is ongoing, should just re-call ourselves
        :return:
        """
        from portal.plugins.gnmdownloadablelink.tasks import TranscodeRequested, NeedsRetry
        from portal.plugins.gnmdownloadablelink.models import DownloadableLink
        from boto.s3.key import Key
        from gnmvidispine.vs_shape import VSShape
        from gnmvidispine.vs_item import VSItem

        mock_item = MagicMock(target=VSItem)
        mock_item.populate = MagicMock()
        mock_item.get = MagicMock(return_value="item title here")
        mock_shape = MagicMock(target=VSShape)

        mock_s3key = MagicMock(target=Key)
        mock_s3key.set_canned_acl = MagicMock()
        mock_s3key.generate_url = MagicMock(return_value="https://fake-download-url")
        mock_s3key.key = "path/to/uploaded_file"

        mdl_before = DownloadableLink.objects.get(item_id="VX-16", shapetag="mezzanine")
        self.assertEqual(mdl_before.status, "Transcoding")

        with patch("gnmvidispine.vs_item.VSItem", return_value=mock_item):
            with patch("portal.plugins.gnmdownloadablelink.tasks.get_shape_for", side_effect=NeedsRetry) as mock_get_shape:
                with patch("portal.plugins.gnmdownloadablelink.tasks.upload_to_s3") as mock_upload:
                    with patch("portal.plugins.gnmdownloadablelink.tasks.create_link_for.apply_async") as mock_apply:
                        from portal.plugins.gnmdownloadablelink.tasks import create_link_for
                        result = create_link_for("VX-16", "mezzanine", obfuscate=False)

                        mock_item.populate.assert_called_once_with('VX-16', specificFields=['title'])
                        mock_get_shape.assert_called_once_with(mock_item,"mezzanine",allow_transcode=False)
                        mock_upload.assert_not_called()
                        mock_s3key.generate_url.assert_not_called()
                        mock_apply.assert_called_once_with(('VX-16', 'mezzanine'), countdown=30, kwargs={'obfuscate': False, 'is_update': True})

                        mdl_after = DownloadableLink.objects.get(item_id="VX-16", shapetag="mezzanine")
                        self.assertEqual(mdl_after.status, "Transcoding")
                        self.assertEqual(mdl_after.public_url, '')
                        self.assertEqual(mdl_after.s3_url, "")


class TestGetVSFileExtension(django.test.TestCase):
    def test_get_vsfile_extension(self):
        from gnmvidispine.vs_storage import VSFile
        from portal.plugins.gnmdownloadablelink.tasks import get_vsfile_extension

        mock_file = MagicMock(target=VSFile)
        mock_file.uri = "http://some/path/to/filename.ext"

        result = get_vsfile_extension(mock_file)
        self.assertEqual(result,"ext")

    def test_get_vsfile_extension_none(self):
        from gnmvidispine.vs_storage import VSFile
        from portal.plugins.gnmdownloadablelink.tasks import get_vsfile_extension

        mock_file = MagicMock(target=VSFile)
        mock_file.uri = "http://some/path/to/filename"

        result = get_vsfile_extension(mock_file)
        self.assertEqual(result,None)


class TestRemoveExpiredLinkFiles(django.test.TestCase):
    fixtures = [
        "links"
    ]

    def test_remove_expired_link_files(self):
        """
        remove_expired_link_files should call remove_file_from_s3 for each file past expiry
        :return:
        """
        from datetime import datetime

        with patch('portal.plugins.gnmdownloadablelink.tasks.remove_file_from_s3') as mock_remove:
            from portal.plugins.gnmdownloadablelink.tasks import remove_expired_link_files
            result = remove_expired_link_files(since=datetime(2018, 1, 6, 19,00,00)) #fake "now" time, for consistent testing

            mock_remove.assert_any_call('s3://bucket_name/path/to/file.ext')
            self.assertEqual(mock_remove.call_count, 1)
            self.assertEqual(result, "Deleted 5 of 5 files")


class TestRemoveFileFromS3(django.test.TestCase):
    def test_remove_file_from_s3_valid(self):
        """
        remove_file_from_s3 should retrieve the bucket and key references then make a delete request to the item identified
        in the URL
        :return:
        """
        fake_connection = MagicMock()
        fake_connection.delete_object = MagicMock()

        with patch("portal.plugins.gnmdownloadablelink.tasks.s3_connect_lowerlevel", return_value=fake_connection) as mock_connect:
            from portal.plugins.gnmdownloadablelink.tasks import remove_file_from_s3

            result = remove_file_from_s3("s3://mybucket/path/to/my/file.ext")

            fake_connection.delete_object.assert_called_once_with(Bucket="mybucket",Key="path/to/my/file.ext")


    def test_remove_file_from_s3_invalid_scheme(self):
        """
        remove_file_from_s3 should raise ValueError if the passed URL is not an S3 url
        :return:
        """
        fake_connection = MagicMock()
        fake_connection.delete_object = MagicMock()

        with patch("portal.plugins.gnmdownloadablelink.tasks.s3_connect_lowerlevel", return_value=fake_connection) as mock_connect:
            from portal.plugins.gnmdownloadablelink.tasks import remove_file_from_s3

            with self.assertRaises(ValueError) as raised_excep:
                result = remove_file_from_s3("http://myserver.com/some/other/url")
            self.assertEqual(str(raised_excep.exception),"Provided URL is not an S3 URL")

    def test_remove_file_from_s3_nofilepath(self):
        """
        remove_file_from_s3 should raise ValueError if the passed URL does not contain a filepath
        :return:
        """
        fake_connection = MagicMock()
        fake_connection.delete_object = MagicMock()

        with patch("portal.plugins.gnmdownloadablelink.tasks.s3_connect", return_value=fake_connection) as mock_connect:
            from portal.plugins.gnmdownloadablelink.tasks import remove_file_from_s3

            with self.assertRaises(ValueError) as raised_excep:
                result = remove_file_from_s3("s3://mybucket")
            self.assertEqual(str(raised_excep.exception),"No file provided to delete")
