import logging


class GridBase(object):
    logger = logging.getLogger("grid_api.GridBase")
    cert_verification = False

    class HttpError(StandardError):
        def __init__(self, code, response_content, response_headers, request_headers, uri, method, *args,**kwargs):
            import json
            super(GridBase.HttpError,self).__init__(*args,**kwargs)
            self.code = code
            self.response_content = response_content
            self.response_headers = response_headers
            self.request_headers = request_headers
            self.uri = uri
            self.method = method

            try:
                self.exception_info = json.loads(response_content)
                self.grid_error_code = self.exception_info['errorKey']
                self.grid_error_message = self.exception_info['errorMessage']
            except StandardError:
                self.exception_info = {}
                self.grid_error_code = '(unknown)'
                self.grid_error_message = '(unknown)'

        def __unicode__(self):
            if len(self.exception_info) > 0:
                return u'{0}: {1}, {2}'.format(self.code, self.grid_error_code, self.grid_error_message)
            else:
                return u'HTTP error {0} performing {1} on {2}\n"{3}'.format(self.code,self.method,self.uri,self.__dict__)

        def __str__(self):
            return self.__unicode__().encode('ASCII')

    def __init__(self, api_key):
        self._api_key=api_key

    def request(self, uri, method="GET", query_params=None, body=None, extra_headers=None):
        import httplib2
        import urllib
        import json
        from pprint import pprint

        headers = {
            'X-Gu-Media-Key': self._api_key,
            'Accept': 'application/json'
        }

        pprint(headers)
        if extra_headers is not None and isinstance(extra_headers,dict):
            headers.update(extra_headers)

        pprint(extra_headers)
        pprint(headers)
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
        h=httplib2.Http(disable_ssl_certificate_validation=not self.cert_verification)
        self.logger.debug("URL is {0}".format(full_uri))
        (resp_headers, content) = h.request(full_uri,method,body,headers)
        if int(resp_headers['status']) < 200 or int(resp_headers['status']) > 299:
            raise self.HttpError(int(resp_headers['status']),content,resp_headers,headers,uri,method)

        try:
            return json.loads(content)
        except ValueError:
            return content


class GridLoader(GridBase):
    logger = logging.getLogger('grid_api.GridLoader')
    _base_uri = 'https://loader.media.test.dev-gutools.co.uk'

    def __init__(self,client_name,*args,**kwargs):
        super(GridLoader,self).__init__(*args,**kwargs)
        self._client_name = client_name

    def upload_image(self, fp, identifiers=None, filename=None):
        import io
        import os.path

        if not isinstance(fp, io.IOBase) and not isinstance(fp,file):
            raise TypeError("fp should be a file-like object returned by open() (was {0})".format(fp.__class__))
        # if filename is None:
        #     if not isinstance(fp,io.FileIO):
        #         self.logger.warning("Unable to determine filename from a non-file type stream")
        #     else:
        #         filename = fp.name
        if filename is None:
            filename = os.path.basename(fp.name)

        qp = {'uploaded_by': self._client_name,
              'filename': filename
              }

        if isinstance(identifiers,list):
            qp['identifiers'] = ",".join(identifiers)
        elif identifiers is not None:
            qp['identifiers'] = identifiers


        response = self.request("{0}/images".format(self._base_uri),method="POST",
                     query_params=qp,
                     body=fp.read(),
                     extra_headers={'Content-Type': 'application/octet-stream'}
                     )

        if 'uri' in response:
            return GridImage(response['uri'], self._api_key) #this is normally the only thing returned
        return response


class GridImage(GridBase):
    logger = logging.getLogger('grid_api.GridImage')
    _base_uri = 'https://api.media.test.dev-gutools.co.uk/images'
    max_cache_time = 30 #in seconds

    def __init__(self,uri_or_id,*args,**kwargs):
        import re
        super(GridImage,self).__init__(*args,**kwargs)

        if re.match(r'^https*://',uri_or_id):
            self.uri = uri_or_id
        else:
            if re.match(r'^[^\w\d]+$', uri_or_id):
                raise ValueError("uri_or_id should be a URL or a hexadecimal grid ID")
            self.uri = self._base_uri + '/' + uri_or_id

        self._info_cache_time = None
        self._info_cache = None

    @property
    def actions(self):
        data=self.info()
        return map(lambda x: x['name'], data['actions'])

    @property
    def links(self):
        data=self.info()
        return map(lambda x:x['rel'], data['links'])

    @property
    def usage_rights_link(self):
        data=self.info()
        return data['data']['userMetadata']['data']['usageRights']['uri']

    def info(self):
        import time
        if self._info_cache is not None:
            if self._info_cache_time > time.time() - self.max_cache_time:
                return self._info_cache

        self._info_cache = self.request(self.uri)
        self._info_cache_time = time.time()
        return self._info_cache

    def delete(self):
        return self.request(self.uri,"DELETE")

    def set_metadata(self, new_md):
        import json

        if not isinstance(new_md, dict):
            raise ValueError("set_metadata expects a dictionary of metadata key/value to set")

        info = self.info()
        md_uri = info['data']['userMetadata']['data']['metadata']['uri']
        body_doc = json.dumps({'data': new_md})
        self.request(md_uri,'PUT',query_params=None,body=body_doc,extra_headers={'Content-Type': 'application/json'})

    def set_usage_rights(self, category="", source=""):
        import json
        md = json.dumps({'data': {'category': category, 'source': source}})

        self.request(self.usage_rights_link,method="PUT",body=md,extra_headers={'Content-Type': 'application/json'})

if __name__ == '__main__':
    import sys
    import time
    from pprint import pprint
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Running tests on grid_api classes")

    logging.info("Attempting to upload {0}".format(sys.argv[1]))

    l = GridLoader('pluto_grid_api_test','pluto-35495dd119156ab447ab8719e1218983a33d3952')

    with open(sys.argv[1]) as fp:
        image = l.upload_image(fp, ['testimage'])
    #pprint(image)
    #pprint(image.info())
    time.sleep(1)
    print "Image supports: {0} and {1}".format(image.actions,image.links)
    image.set_metadata({'credit': 'Andy Gallagher', 'description': 'Test image'})
    time.sleep(1)
    print "Image supports: {0} and {1}".format(image.actions, image.links)
    #image.delete()