import logging


class GridBase(object):
    class HttpError(StandardError):
        def __init__(self, code, response_content, response_headers, request_headers, uri, method, *args,**kwargs):
            super(GridBase.HttpError,self).__init__(*args,**kwargs)
            self.code = code
            self.response_content = response_content
            self.response_headers = response_headers
            self.request_headers = request_headers
            self.uri = uri
            self.method = method

        def __unicode__(self):
            return u'HTTP error {0} performing {1} on {2}\n"{3}'.format(self.code,self.method,self.uri,self.__dict__)

        def __str__(self):
            return self.__unicode__().encode('ASCII')

    def __init__(self, api_key):
        self._api_key=api_key

    def request(self, uri, method="GET", query_params=None, body=None, extra_headers=None):
        import httplib2
        import urllib
        import json

        headers = {
            'X-Gu-Media-Key': self._api_key,
            'Accept': 'application/json'
        }

        if extra_headers is not None and not isinstance(extra_headers,dict):
            headers.update(extra_headers)

        if query_params is not None and not isinstance(query_params,dict):
            raise TypeError("query_params must be a dictionary")

        # p = []
        # if query_params is not None:
        #     for k,v in query_params.items():
        #         p.append("{0}={1}".format(urllib.quote(k,''),urllib.quote(v,'')))

        full_uri = uri
        if query_params is not None and len(query_params)>0:
            full_uri += "?"+urllib.urlencode(query_params)

        #https://loader.media.test.dev-gutools.co.uk/images{?uploadedBy,identifiers,uploadTime,filename}
        h=httplib2.Http()
        (resp_headers, content) = h.request(full_uri,method,body,headers)
        if int(resp_headers['status']) < 200 or int(resp_headers['status']) > 299:
            raise self.HttpError(int(resp_headers['status']),content,resp_headers,headers,uri,method)

        return json.loads(content)


class GridLoader(GridBase):
    logger = logging.getLogger('grid_api.GridLoader')
    _base_uri = 'https://loader.media.test.dev-gutools.co.uk'

    def __init__(self,client_name,*args,**kwargs):
        super(GridLoader,self).__init__(*args,**kwargs)
        self._client_name = client_name

    def upload_image(self, fp, identifiers, filename=None):
        import io
        import os.path

        if not isinstance(fp,io.IOBase) and not isinstance(fp,file):
            raise TypeError("fp should be a file-like object returned by open() (was {0})".format(fp.__class__))
        # if filename is None:
        #     if not isinstance(fp,io.FileIO):
        #         self.logger.warning("Unable to determine filename from a non-file type stream")
        #     else:
        #         filename = fp.name
        filename = os.path.basename(fp.name)

        if isinstance(identifiers,list):
            id_string = ",".join(identifiers)
        else:
            id_string = identifiers

        response = self.request("{0}/images".format(self._base_uri),method="POST",
                     query_params={
                        'uploaded_by': self._client_name,
                        'filename': filename
                     },
                     body=fp.read(),
                     extra_headers={'Content-Type': 'application/octet-stream'}
                     )

        if 'uri' in response:
            return GridImage(response['uri'],self._api_key) #this is normally the only thing returned
        return response


class GridImage(GridBase):
    logger = logging.getLogger('grid_api.GridImage')
    _base_uri = 'https://api.media.test.dev-gutools.co.uk/images'

    def __init__(self,uri_or_id,*args,**kwargs):
        import re
        super(GridImage,self).__init__(*args,**kwargs)

        if re.match(r'^https*://',uri_or_id):
            self.uri = uri_or_id
        else:
            if re.match(r'^[^\w\d]+$', uri_or_id):
                raise ValueError("uri_or_id should be a URL or a hexadecimal grid ID")
            self.uri = self._base_uri + '/' + uri_or_id

    def info(self):
        return self.request(self.uri)

if __name__ == '__main__':
    import sys
    from pprint import pprint
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Running tests on grid_api classes")

    logging.info("Attempting to upload {0}".format(sys.argv[1]))

    l = GridLoader('pluto_grid_api_test','')

    with open(sys.argv[1]) as fp:
        image = l.upload_image(fp, '')
    pprint(image)
    pprint(image.info())