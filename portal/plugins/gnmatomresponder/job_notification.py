import lxml.etree as ET
from xml.sax.saxutils import unescape
import re

pair_splitter = re.compile(r'^(\w{2}-\d+)=(.*)$')


class JobNotification(object):
    """
    This class abstracts the Vidispine job notification document to allow for easier reading
    """
    ns = "{http://xml.vidispine.com/schema/vidispine}"

    def __init__(self, xmlstring):
        self.parsedContent = ET.fromstring(xmlstring)

    def __getattr__(self, item):
        for keynode in self.parsedContent.findall("{ns}field/{ns}key".format(ns=self.ns)):
            if keynode.text==item:
                valnode = keynode.find("../{ns}value".format(ns=self.ns))
                if valnode is not None:
                    return valnode.text
        return None

    def __str__(self):
        return "{type} job for {filename} by {user}".format(type=self.type,filename=self.originalFilename,user=self.username)

    def parsed_job_document(self):
        return JobDocument(unescape(self.jobDocument))

    def file_paths(self):
        """
        returns a dictionary of relative file path/file ID pairs, from the filePathMap parameter
        :return: dictionary
        """
        if self.filePathMap is None:
            return None

        pairs = self.filePathMap.split(',')

        def split_pair(pair): #can't be sure that there will be no = in the filename
            result = pair_splitter.match(pair)
            if result:
                return (result.group(1), result.group(2))
            else:
                return None

        return dict(filter(lambda result: result is not None, map(lambda pair: split_pair(pair),pairs)))


class JobDocument(object):
    """
    This class abstracts the Vidipsine job document to allow for easier reading
    """
    ns = "{http://xml.vidispine.com/schema/vidispine}"

    def __init__(self, xmlstring):
        self.parsedContent = ET.fromstring(xmlstring)

    def dump(self):
        print ET.tostring(self.parsedContent)