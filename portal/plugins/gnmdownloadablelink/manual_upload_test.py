#!/usr/bin/env python

from tasks import singlepart_upload_vsfile_to_s3, multipart_upload_vsfile_to_s3
import logging
from optparse import OptionParser
from gnmvidispine.vs_storage import VSStorage
from django.conf import settings

logging.basicConfig(level=logging.DEBUG)
botolgr = logging.getLogger("botocore")
botolgr.level = logging.WARN

###START MAIN
parser = OptionParser()
parser.add_option("-f","--file-id", dest="fileid", help="Test with this file ID from Vidispine")
parser.add_option("-s", "--storage-id", dest="storageid", help="Storage that the test file lives on")
parser.add_option("--multipart", dest="multipart", action="store_true", help="Test multipart upload. If not specified, tests singlepart upload")
(options, args) = parser.parse_args()

storage = VSStorage(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
if not options.storageid:
    raise ValueError("You must specify a storage with the --storage-id option")

storage.populate(options.storageid)

if not options.fileid:
    raise ValueError("You must specify a file ID with the --file-id option")

file_ref = storage.fileForID(options.fileid)

if options.multipart:
    multipart_upload_vsfile_to_s3(file_ref, file_ref.name, "application/octet-stream")
else:
    singlepart_upload_vsfile_to_s3(file_ref, file_ref.name, "application/octet-stream")
