import unittest2
from mock import MagicMock, patch
import os


class TestJobNotification(unittest2.TestCase):
    @staticmethod
    def _get_test_data(filename):
        mypath = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(mypath, "data", filename)) as f:
            return f.read()

    def test_read_data(self):
        """
        JobNotification should read the provided XML and allow simple access to key/value data
        :return:
        """
        from portal.plugins.gnmatomresponder.job_notification import JobNotification
        j = JobNotification(self._get_test_data("sample_notification.xml"))

        self.assertEqual(j.jobId,"VX-22")
        self.assertEqual(j.status,"FINISHED_WARNING")
        self.assertEqual(j.transcoder, "http://127.0.0.1:8888/")
        self.assertEqual(j.invalidKey, None)

    def test_invalid_xml(self):
        """
        JobNotification should raise XMLSyntaxError if not passed valid xml
        :return:
        """
        from portal.plugins.gnmatomresponder.job_notification import JobNotification
        from lxml.etree import XMLSyntaxError

        with self.assertRaises(XMLSyntaxError):
            j = JobNotification("dsadsjkhadsjkhdasadmnsbnmadsmnbdasbmndasadsdasydaskjhdasnbfKNMGAWMN.,BEGM,N.GAE")

    def test_file_paths(self):
        """
        JobNotification should decode the filePathMap parameter to a dictionary of fileid->relative path pairs
        :return:
        """
        from portal.plugins.gnmatomresponder.job_notification import JobNotification
        j = JobNotification(self._get_test_data("sample_notification.xml"))

        self.assertDictEqual(j.file_paths(),{'VX-27': 'Call of Duty Modern Warfare Remastered  Launch Trailer  PS4.mp4',
                                             'VX-30': 'Call of Duty Modern Warfare Remastered  Launch Trailer  PS4_lowres.mp4'})