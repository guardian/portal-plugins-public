import django.test
from mock import MagicMock, patch, call


class TestChunkedDownloader(django.test.TestCase):
    class MockResponse(object):
        def __init__(self, code, content, headers={}):
            self.status_code = code
            self.content = content
            self.headers = headers

            if not 'Content-Length' in headers:
                self.headers.update({'Content-Length': len(self.content)})

    def test_init_ok(self):
        """
        ChunkedDownloader should
        :return:
        """
        with patch('requests.head', return_value=self.MockResponse(200,"", {'Content-Length':20})) as mock_head:
            from portal.plugins.gnmdownloadablelink.chunked_downloader import ChunkedDownloader

            d = ChunkedDownloader("http://some/url", chunksize=1024, auth=('username','password'))

            mock_head.assert_called_once_with("http://some/url", auth=('username', 'password'))
            self.assertEqual(d.chunksize, 1024)
            self.assertEqual(d.total_length,20)

    def test_init_redirect(self):
        """
        ChunkedDownloader should follow redirect requests to get to the ultimately correct url
        :return:
        """
        with patch('requests.head', side_effect=[
                self.MockResponse(303,"",{'Location': "http://some/other/url"}),
                self.MockResponse(200,"",{'Content-Length': 15})
            ]) as mock_head:

            from portal.plugins.gnmdownloadablelink.chunked_downloader import ChunkedDownloader

            d = ChunkedDownloader("http://some/url", chunksize=1024, auth=('username','password'))

            mock_head.assert_has_calls([
                call("http://some/url", auth=('username', 'password')),
                call("http://some/other/url", auth=('username', 'password'))
            ])
            self.assertEqual(d.chunksize, 1024)
            self.assertEqual(d.total_length,15)

    def test_init_404(self):
        """
        ChunkedDownloader should raise an HTTPError if the server responds 404 to the initial head request
        :return:
        """
        with patch('requests.head', return_value=self.MockResponse(404,"")) as mock_head:
            from portal.plugins.gnmdownloadablelink.chunked_downloader import ChunkedDownloader, HttpError

            with self.assertRaises(HttpError) as raised_excep:
                d = ChunkedDownloader("http://some/url", chunksize=1024, auth=('username','password'))
            self.assertEqual(raised_excep.exception.code,404)
            self.assertEqual(raised_excep.exception.url,"http://some/url")
            mock_head.assert_called_once_with("http://some/url", auth=('username', 'password'))

    def test_download_chunk_valid(self):
        """
        ChunkedDownloader.get_chunk() should make a get request and return the data retrieved.
        :return:
        """
        with patch('requests.head', return_value=self.MockResponse(200,"", {'Content-Length':20})) as mock_head:
            with patch('requests.get', return_value=self.MockResponse(206,"Conte")) as mock_get:
                from portal.plugins.gnmdownloadablelink.chunked_downloader import ChunkedDownloader

                d = ChunkedDownloader("http://some/url", chunksize=5, auth=('username','password'))

                mock_head.assert_called_once_with("http://some/url", auth=('username', 'password'))
                self.assertEqual(d.chunksize, 5)
                self.assertEqual(d.total_length,20)

                result = d.get_chunk(0)
                mock_get.assert_called_once_with("http://some/url", auth=('username', 'password'), headers={'Range': 'Bytes=0-4'})
                self.assertEqual(result, "Conte")

    def test_stream_chunk_valid(self):
        """
        ChunkedDownloader.stream_chunk() should make a get request and return a stream to the data retrieved
        :return:
        """
        with patch('requests.head', return_value=self.MockResponse(200,"", {'Content-Length':20})) as mock_head:
            with patch('requests.get', return_value=self.MockResponse(206,"Conte")) as mock_get:
                from portal.plugins.gnmdownloadablelink.chunked_downloader import ChunkedDownloader

                d = ChunkedDownloader("http://some/url", chunksize=5, auth=('username','password'))

                mock_head.assert_called_once_with("http://some/url", auth=('username', 'password'))
                self.assertEqual(d.chunksize, 5)
                self.assertEqual(d.total_length,20)

                result = d.stream_chunk(0)
                mock_get.assert_called_once_with("http://some/url", auth=('username', 'password'), headers={'Range': 'Bytes=0-4'})

                self.assertEqual(result.read(), "Conte")

    def test_download_chunk_invalid(self):
        """
        ChunkedDownloader should raise ChunkDoesNotExist if a chunk is requested beyond the bounds of the data
        :return:
        """
        with patch('requests.head', return_value=self.MockResponse(200,"", {'Content-Length':20})) as mock_head:
            with patch('requests.get', return_value=self.MockResponse(206,"Conte")) as mock_get:
                from portal.plugins.gnmdownloadablelink.chunked_downloader import ChunkedDownloader, ChunkDoesNotExist

                d = ChunkedDownloader("http://some/url", chunksize=5, auth=('username','password'))

                mock_head.assert_called_once_with("http://some/url", auth=('username', 'password'))
                self.assertEqual(d.chunksize, 5)
                self.assertEqual(d.total_length,20)

                with self.assertRaises(ChunkDoesNotExist) as raised:
                    result = d.get_chunk(5)
                mock_get.assert_not_called()    #the check for bounds is carried out before the get request is sent
                self.assertEqual(raised.exception.chunknum, 5)
                self.assertEqual(raised.exception.chunksize, 5)

