import datetime
import logging
import os.path

import unittest2
from boto import kinesis
from django.core.management import execute_manager
from mock import patch

logging.basicConfig(level=logging.DEBUG)

import django_test_settings as django_test_settings

class TestImporter(unittest2.TestCase):
    pass