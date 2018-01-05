import requests
import logging
import io
import hashlib

DEFAULT_CHUNKSIZE=1024*1024

logger = logging.getLogger(__name__)


class HttpError(RuntimeError):
    def __init__(self, code, url, request_headers, response_headers, response_body, content_type):
        self.code = code
        self.url = url
        self.request_headers = request_headers
        self.response_headers = response_headers
        self.response_body = response_body
        self.content_type = content_type

    def __str__(self):
        return "HTTP error {0} accessing {1}: {2}".format(self.code, self.url, self.response_body)


class ChunkDoesNotExist(RuntimeError):
    """
    Exception raised if you try to download a chunk that is beyond the length of the target object
    (as determined by a HEAD request when you initialise the class)
    """
    def __init__(self, chunknum, chunksize):
        self.chunknum = chunknum
        self.chunksize = chunksize

    def __str__(self):
        return "Chunk {0} of size {1} is beyond the length of the downloading object".format(self.chunknum,self.chunksize)


class ChunkedDownloader(object):
    """
    Self-rolled chunk downloader, to try to understand what is happening during downloads
    """
    def __init__(self, url, chunksize=DEFAULT_CHUNKSIZE, enable_hashing=True, **kwargs):
        """
        Set it up
        :param url: url to access
        :param chunksize: chunk size to use
        :param kwargs: extra args for requests head and get
        """
        self.url = url
        self.redirected_url = None
        self.kwargs = kwargs
        self.chunksize=chunksize
        self.total_length = 0
        if enable_hashing:
            self.checksummer = hashlib.sha1()
        else:
            self.checksummer = None

        test_url = self.url
        while True:
            result = requests.head(test_url,**kwargs)
            logger.debug("ChunkedDownloader: headers for {0} are {1}".format(url, result.headers))
            self.total_length = int(result.headers['Content-Length'])

            if result.status_code==303: #follow redirect loop
                self.redirected_url = result.headers['Location']
                test_url = self.redirected_url
            elif result.status_code<200 or result.status_code>299:
                raise HttpError(result.status_code, url, {}, result.headers, result.content, None)
            else:
                break

    def get_chunk(self, chunk_number):
        """
        Buffer a chunk of data and return it
        :param chunk_number: chunk to get. Range is from (chunk_number*chunk_size)->((chunk_number+1)*chunk_size)-1, so zero-based
        :return: buffer of data
        """
        kwargs = self.kwargs
        if 'headers' in kwargs:
            current_headers = kwargs['headers']
        else:
            current_headers = {}

        start_byte = chunk_number*self.chunksize
        if start_byte > self.total_length:
            raise ChunkDoesNotExist(chunk_number, self.chunksize)

        current_headers['Range'] = "Bytes={0}-{1}".format(chunk_number*self.chunksize, (chunk_number+1)*self.chunksize-1)
        kwargs['headers'] = current_headers

        if self.redirected_url:
            target_url = self.redirected_url
        else:
            target_url = self.url

        logger.debug("Headers: {0}".format(current_headers))
        result = requests.get(target_url,**kwargs)
        logger.info("Chunk for {0} returned {1}".format(current_headers['Range'], result.status_code))
        if result.status_code==200:
            logger.warning("Server responded 200 to a partial download request, expected 206. This could indicate a misconfiguration")
        elif result.status_code!=206: #expect status_code 206, partial content
            raise HttpError(result.status_code, target_url, {}, result.headers, result.content, None)

        if self.checksummer is not None:
            self.checksummer.update(result.content)
        return result.content

    def stream_chunk(self,chunk_number):
        """
        convenience method that returns a stream to a memory buffer of a chunk
        :param chunk_number:
        :return: BytesIO stream of the buffered chunk
        """
        return io.BytesIO(self.get_chunk(chunk_number))

    def final_checksum(self):
        """
        Returns a hexadecimal printable string of the final sha-1 checksum of everything downloaded
        :return:
        """
        if self.checksummer is None:
            raise RuntimeError("Can't provide final checksum when checksumming is not enabled!")
        return self.checksummer.hexdigest()