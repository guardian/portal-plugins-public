import xml.etree.cElementTree as ET
import re


class VSException(StandardError):
    def __init__(self,*args,**kwargs):
        super(VSException,self).__init__(*args,**kwargs)
        self.request_url = None
        self.request_body = None
        self.request_method = None
        self.exceptionType="Not from Vidispine"
        self.exceptionWhat="Unknown"
        self.exceptionID="Unknown"
        self.exceptionContext = "Unknown"
        self.exceptionRawXML = ""

    @staticmethod
    def getNodeContent(xmlnode,nodename,default=""):
        n = xmlnode.find(nodename)
        if n is not None:
            return n.text

        return default

    def fromJSON(self,jsondata):
        """
        Given a JSON string from a Vidispine error response, populate this exception
        """
        import json
        self.exceptionType="Not from Vidispine"
        self.exceptionWhat="Unknown"
        self.exceptionID="Unknown"
        self.exceptionContext = "Unknown"
        self.exceptionRawXML = jsondata

        try:
            info=json.loads(jsondata)
            for k,v in info.items():
                if v is not None:
                    self.exceptionWhat=k
                    self.exceptionType=v['type']
                    self.exceptionID=v['id']
                    self.exceptionContext=v['context']
        except Exception as e:
            raise e

    def fromXML(self,xmldata):
        """
        Given a parsed XML document from a Vidispine error response, populate this exception
        :param xmldata: root node of a parsed ElementTree document containing error information from Vidispine
        """
        self.exceptionType="Not from Vidispine"
        self.exceptionWhat="Unknown"
        self.exceptionID="Unknown"
        self.exceptionContext = "Unknown"
        self.exceptionRawXML = xmldata

        try:
            exceptionData = ET.fromstring(xmldata)
            #root = exceptionData.getroot()

            for child in exceptionData:
                self.exceptionType = child.tag
                self.exceptionType = re.sub(r'{[^}]+}','',self.exceptionType)
                self.exceptionWhat = self.getNodeContent(child,'{0}explanation'.format('{http://xml.vidispine.com/schema/vidispine}'),default="no explanation provided")
                self.exceptionID = self.getNodeContent(child,'{0}id'.format('{http://xml.vidispine.com/schema/vidispine}'),default="no id provided")
                self.exceptionContext = self.getNodeContent(child,'{0}context'.format('{http://xml.vidispine.com/schema/vidispine}'),default="no context provided")
        except Exception as e:
            #raise InvalidData("Not given Vidispine exception XML")
            raise e

    def to_json(self):
        from django.conf import settings
        import json
        from traceback import format_exc

        if settings.DEBUG:
            info = json.dumps({'status': 'error', 'error': str(self), 'traceback': format_exc()})
        else:
            info = json.dumps({'status': 'error', 'error': str(self)})

        return info

    def __str__(self):
        """
        Return a string representation of the exception
        """
        if self.exceptionType:
            rtn = "Vidispine exception %s\n" % self.__class__.__name__
            rtn += "\tType: %s\n\tContext: %s\n\tWhat: %s\n\tID: %s\n" % (self.exceptionType,self.exceptionContext,self.exceptionWhat,self.exceptionID)
            rtn += "\nReturned XML: %s\n" % (self.exceptionRawXML)
            return rtn

        return self.message