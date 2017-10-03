class HttpError(StandardError):
    def __init__(self,response,content):
        self.response=response
        self.content=content

    def __unicode__(self):
        return u"HTTP {0} error: {1}".format(self.response['status'],self.content)

    @property
    def code(self):
        return int(self.response['status'])

    @property
    def status(self):
        return self.code

class VSApi(object):
    def __init__(self,host="localhost",port=8080,username="admin",password="",protocol="http",url=None,cache=None):
        import re

        if protocol != "http" and protocol != "https":
            raise ValueError("protocol is not valid")

        if url is not None:
            parts = re.match(r'([^:]+)://(.*)$',url)
            protocol = parts.group(1)
            host = parts.group(2)

        self.host = host
        try:
            self.port = int(port)
        except StandardError:
            self.port = port

        self.username = username
        self.password = password
        self.protocol = protocol
        self._xmlns = "{http://xml.vidispine.com/schema/vidispine}"
        self._cache = cache
        self.cache_timeout = 30 #in seconds

    def _validate_params(self):
        import re

        if re.search(u'[/:]',self.host):
            raise ValueError("host is not valid")
        if not isinstance(self.port,int):
            raise ValueError("port is not valid")
        if self.protocol != "http" and self.protocol != "https":
            raise ValueError("protocol is not valid")

    def request(self,path,method="GET",body=None,content_type=None):
        from httplib2 import Http
        import xml.etree.ElementTree as ET
        from xml.parsers.expat import ExpatError
        h = Http()

        h.add_credentials(self.username,self.password)

        self._validate_params()
        uri = "{0}://{1}:{2}/API/{3}".format(self.protocol,self.host,self.port,path)

        headers = {'Accept': 'application/xml'}
        if content_type is not None:
            headers['Content-Type']=content_type

        if body is None:
            (response,content) = h.request(uri, method=method, headers=headers)
        else:
            (response,content) = h.request(uri, method=method, body=body, headers=headers)

        if int(response['status']) < 200 or int(response['status']) > 299:
            raise HttpError(response, content)

        #register default namespace as vidispine, http://stackoverflow.com/questions/8983041/saving-xml-files-using-elementtree
        #ET.register_namespace('', "http://xml.vidispine.com/schema/vidispine")
        #ET._namespace_map['']="http://xml.vidispine.com/schema/vidispine"
        try:
            return ET.fromstring(content)
        except ExpatError:
            return content

class VSLibraryCollection(VSApi):
    def __init__(self, host="localhost", port=8080, username="admin", password="", protocol="http", url=None, cache=None):
        """
        Create a new connection to Vidispine to get library information
        :param host: Host for Vidispine. Defaults to localhost.
        :param port: Port on which Vidispine is running. Defaults to 8080
        :param username: Username to communicate with Vidispine. Default is admin
        :param password: Password for the user
        :param protocol: http (default) or https, to talk to Vidispine
        :return: None
        """
        super(VSLibraryCollection,self).__init__(host,port,username,password,protocol,url,cache)
        self.page_size = 10
        self.count = 0

    def cache_invalidate(self):
        uri = "library;number={0};first={1}".format(self.page_size, (self.page_size * 0)+1)
        self._cache.delete("portal.plugins.gnmlibrarytool:{0}".format(uri))
        self._cache.delete("portal.plugins.gnmlibrarytool:{0};autoRefresh=true".format(uri))
        self._cache.delete("portal.plugins.gnmlibrarytool:{0};autoRefresh=false".format(uri))

    def scan(self,autoRefresh=None,page=0):
        """
        Scans for libraries in Vidispine as a generator, yielding the library name
        :param autoRefresh: Can be None, True or False.  If True or False then only look for libraries that are (or are not) auto-refreshing.
        """
        import logging

        if not isinstance(page,int):
            raise ValueError("page must be an integer")
        if not isinstance(self.page_size,int):
            raise ValueError("page_size must be an integer")

        uri = "library;number={0};first={1}".format(self.page_size, (self.page_size * page)+1)

        if autoRefresh is not None:
            if autoRefresh:
                uri += ";autoRefresh=true"
            else:
                uri += ";autoRefresh=false"

        logging.info("request uri is %s" % uri)
        doc = None
        if self._cache is not None:
            doc = self._cache.get("portal.plugins.gnmlibrarytool:{0}".format(uri))
        if doc is None:
            doc = self.request(uri,method="GET")
            self._cache.set("portal.plugins.gnmlibrarytool:{0}".format(uri),doc,self.cache_timeout)

        try:
            node = doc.find("{0}hits".format(self._xmlns))
            self.count = int(node.text)
        except StandardError:
            pass

        for node in doc.findall("{0}uri".format(self._xmlns)):
            yield node.text

    @property
    def page_count(self):
        if self.page_size < 1:
            return ValueError("Page size is zero")
        return self.count/self.page_size

class VSLibrary(VSApi):
    """
    This class represents a Vidispine library, handling all requisite XML parsing via ElementTree
    """

    def __init__(self, host="localhost", port=8080, username="admin", password="", protocol="http", url=None, cache=None):
        """
        Create a new connection to Vidispine to get library information
        :param host: Host for Vidispine. Defaults to localhost.
        :param port: Port on which Vidispine is running. Defaults to 8080
        :param username: Username to communicate with Vidispine. Default is admin
        :param password: Password for the user
        :param protocol: http (default) or https, to talk to Vidispine
        :return: None
        """
        super(VSLibrary,self).__init__(host,port,username,password,protocol,url,cache)

        self._document = None
        self._settings = None
        self._storagerule = None

    def get_hits(self, vsid):
        """
        Loads enough of the library definition to get the total number of hits
        :param vsid: ID of the vidispine library.  Raises ValueError if this is not in {site}-{number} format.
        :return: Integer representing number of items referenced by library.  This is a convenience, the same result
        can be obtained by reading the VSlibrary.hits property after calling this method
        """
        import re
        if not re.match(r'^\w{2}\*\d+$',vsid):
            raise ValueError("{0} is not a valid Vidispine library ID".format(vsid))

        if self._cache is not None:
            self._document = self._cache.get("portal.plugins.gnmlibrarytool:{0}:document".format(vsid))
        if self._document is None:
            self._document = self.request("library/{0};number=0".format(vsid))
            if self._cache is not None: self._cache.set("portal.plugins.gnmlibrarytool:{0}:document".format(vsid),self._document,self.cache_timeout)

        return self.hits

    def delete(self):
        import re
        if self.vsid is None or not re.match(r'^\w{2}\*\d+$',self.vsid):
            raise ValueError("{0} is not a valid Vidispine library ID".format(self.vsid))
        self.request('library/{0}'.format(self.vsid),method="DELETE")
        self.cache_invalidate()

    def cache_invalidate(self):
        if self._cache:
            self._cache.delete("portal.plugins.gnmlibrarytool:{0}:document".format(self.vsid))
            self._cache.delete("portal.plugins.gnmlibrarytool:{0}:settings".format(self.vsid))
            self._cache.delete("portal.plugins.gnmlibrarytool:{0}:storagerule".format(self.vsid))

    @staticmethod
    def _basicSearchDoc():
        from xml.etree.ElementTree import Element, SubElement
        root = Element("ItemSearchDocument",attrib={'xmlns': 'http://xml.vidispine.com/schema/vidispine'})
        fieldNode = SubElement(root,"field")
        nameNode = SubElement(fieldNode,"name")
        nameNode.text = "gnm_asset_category"
        valueNode = SubElement(fieldNode,"value")
        valueNode.text = "replace_me"
        return root

    def create_new(self):
        """
        Creates a new, blank library with a default search
        :return: None
        """
        import xml.etree.ElementTree as ET

        self.cache_invalidate()
        doc = self._basicSearchDoc()


        resultdoc = self.request("item?result=library",method="PUT",body=ET.tostring(doc,encoding="UTF-8"),content_type='application/xml')

        libNode = resultdoc.find('{0}library'.format(self._xmlns))
        if libNode is None:
            raise StandardError("Invalid response from Vidispine, no <library> node")
        self.populate(libNode.text)

    def populate(self, vsid):
        """
        Load a library definition from Vidispine
        :param vsid: ID of the vidispine library. Raises ValueError if this is not in {site}-{number} format.
        :return: None
        """
        import re
        if not re.match(r'^\w{2}\*\d+$',vsid):
            raise ValueError("{0} is not a valid Vidispine library ID".format(vsid))

        if self._cache is not None:
            self._document = self._cache.get("portal.plugins.gnmlibrarytool:{0}:document".format(vsid))
            self._settings = self._cache.get("portal.plugins.gnmlibrarytool:{0}:settings".format(vsid))
            self._storagerule = self._cache.get("portal.plugins.gnmlibrarytool:{0}:storagerule".format(vsid))

        if self._document is None:
            self._document = self.request("library/{0}".format(vsid))
            if self._cache is not None: self._cache.set("portal.plugins.gnmlibrarytool:{0}:document".format(vsid),self._document,self.cache_timeout)
        if self._settings is None:
            self._settings = self.request("library/{0}/settings".format(vsid))
            if self._cache is not None: self._cache.set("portal.plugins.gnmlibrarytool:{0}:settings".format(vsid),self._settings,self.cache_timeout)
        try:
            if self._storagerule is None:
                self._storagerule = self.request("library/{0}/storage-rule".format(vsid))
                if self._cache is not None: self._cache.set("portal.plugins.gnmlibrarytool:{0}:storagerule".format(vsid),self._storagerule,self.cache_timeout)
        except HttpError as e:
            if e.response.code != 404:
                raise e

    def saveSettings(self):
        """
        Saves the current state of the object back into Vidispine. Errors are reported as HttpExceptions
        :return: None
        """
        import xml.etree.ElementTree as ET
        if self._settings is None:
            raise ValueError("No settings loaded")

        print "XML to set: %s" % ET.tostring(self._settings,encoding="UTF-8")

        self.request("library/{0}/settings".format(self.vsid),method="PUT",
                     body=ET.tostring(self._settings,encoding="UTF-8"),content_type='application/xml'
        )

    def saveStorageRule(self):
        """
        Saves the current state of the storage rules back into Vidispine. Errors are reported as HttpExceptions
        :return: None
        """
        import xml.etree.ElementTree as ET
        if self._storagerule is None:
            raise ValueError("No storage rule loaded")

        #here is where it gets annoying.  We get a StorageRulesDocument, detailing EVERY storage rule,
        #but we have to set them invididually as a StorageRuleDocument (note singular)
        print "storage rule to set:"
        print ET.tostring(self._storagerule,encoding="UTF-8")
        for rule_tag in self._storagerule.findall("{0}tag".format(self._xmlns)):
            tagname = rule_tag.attrib["id"]
            doc = ET.Element("StorageRuleDocument",attrib={'xmlns': 'http://xml.vidispine.com/schema/vidispine'})
            for node in rule_tag:
                doc.append(node)
            print "XML to set for %s: %s" % (tagname,ET.tostring(doc,encoding="UTF-8"))
            self.request('library/{0}/storage-rule/{1}'.format(self.vsid,tagname),
                         body=ET.tostring(doc,encoding="UTF-8"),method="PUT",content_type="application/xml")

    def deleteStorageRule(self, tagname=None):
        """
        Deletes the current storage rule definition associated with the library.
        :param tagname: Delete the storage rule for this tag.  If this is None (the default), delete all storage rules
        :return: None
        """

        if tagname is None:
            self.request('library/{0}/storage-rule'.format(self.vsid), method="DELETE")
        else:
            self.request('library/{0}/storage-rule/{1}'.format(self.vsid,tagname), method="DELETE")

        self.cache_invalidate()

    @property
    def hits(self):
        elem = self._document.find("{0}hits".format(self._xmlns))
        if elem is not None:
            return int(elem.text)
        return None

    @property
    def vsid(self):
        try:
            elem = self._settings.find("{0}id".format(self._xmlns))
        except AttributeError as e:
            elem = self._document.find("{0}id".format(self._xmlns))
        if elem is not None:
            return elem.text
        return None

    @vsid.setter
    def vsid(self,value):
        import re
        if not re.match(r'^\w{2}\*\d+$',value):
            raise ValueError("{0} is not a valid Vidispine library ID".format(value))
        elem = self._settings.find("{0}id".format(self._xmlns))
        if elem is not None:
            elem.text = value
        else:
            raise KeyError("No settings document or it does not contain <id>")

    @property
    def owner(self):
        elem = self._settings.find("{0}username".format(self._xmlns))
        if elem is not None:
            return elem.text
        return None

    @property
    def updateMode(self):
        elem = self._settings.find("{0}updateMode".format(self._xmlns))
        if elem is not None:
            return elem.text
        return None

    @updateMode.setter
    def updateMode(self,value):
        elem = self._settings.find("{0}updateMode".format(self._xmlns))
        if elem is not None:
            elem.text = value
        else:
            raise KeyError("No settings document or it does not contain <updateMode>")

    @property
    def autoRefresh(self):
        elem = self._settings.find("{0}autoRefresh".format(self._xmlns))
        if elem is not None:
            if elem.text == "true":
                return True
            return False
        return None

    @autoRefresh.setter
    def autoRefresh(self,value):
        if not isinstance(value,bool):
            raise ValueError()

        elem = self._settings.find("{0}autoRefresh".format(self._xmlns))
        if elem is not None:
            if value:
                elem.text = "true"
            else:
                elem.text = "false"
        else:
            raise KeyError("No settings document or it does not contain <autoRefresh>")

    @property
    def query(self):
        """
        Get the query section of the library definition
        :return: ElementTree document representing the library's query
        """
        elem = self._settings.find("{0}query".format(self._xmlns))
        if elem is not None:
            return elem
        return None

    @query.setter
    def query(self,value):
        """
        Set the query definition XML.  Expects either a string or an ElementTree
        :return: None
        """
        import xml.etree.ElementTree as ET
        to_set = None
        if isinstance(value,basestring):
            #register default namespace as vidispine, http://stackoverflow.com/questions/8983041/saving-xml-files-using-elementtree
            #ET.register_namespace('',"http://xml.vidispine.com/schema/vidispine")
            #ET._namespace_map['']="http://xml.vidispine.com/schema/vidispine"
            to_set = ET.fromstring(value)
        elif isinstance(value,ET.Element):
            to_set = value
        else:
            raise ValueError("You need to pass a string or an ElementTree element")

        elem = self._settings.find("{0}query".format(self._xmlns))
        if elem is None:
            raise ValueError("No query element present! This object has not been initialised properly")
        self._settings.remove(elem)
        self._settings.append(to_set)
        self.cache_invalidate()

    @property
    def storagerule(self):
        return self._storagerule

    def _stripwhitespace(self,node):
        for x in node:
            #if x.nodeType == Node.TEXT_NODE:
            if x.text is not None:
               x.text = x.text.strip()
            #elif x.nodeType == Node.ELEMENT_NODE:
            self._stripwhitespace(x)
        return node

    @storagerule.setter
    def storagerule(self,value):
        """
        Set the storage rule XML. Expects either a string or an ElementTree
        :param value: String or ElementTree to set
        :return: None
        """
        import xml.etree.ElementTree as ET
        if isinstance(value, basestring):
            ET._namespace_map[''] = "http://xml.vidispine.com/schema/vidispine"
            to_set = ET.fromstring(value)
        #elif isinstance(value, ET.Element):
        else:
            to_set = value
        #else:
        #    raise ValueError("You need to pass a string or an ElementTree element")
        
        self._storagerule = self._stripwhitespace(to_set)
        self.cache_invalidate()
