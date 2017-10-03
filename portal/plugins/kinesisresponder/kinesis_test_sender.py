#!/usr/bin/env python

from boto import kinesis
from boto.kinesis import layer1 as kl1
import json
import hashlib
from time import sleep
from datetime import datetime
from pprint import pprint


STREAM_NAME = 'TestContentAtom2'
#START MAIN
conn = kinesis.connect_to_region('eu-west-1')

if not isinstance(conn,kl1.KinesisConnection): raise TypeError #for Intellij to determine type

# while True:
#     testobject = {
#         'message': 'hello',
#         'timestamp': str(datetime.now())
#     }
#
#     m = hashlib.sha1()
#     content = json.dumps(testobject)
#     m.update(content)
#     conn.put_record(STREAM_NAME,content,partition_key=m.hexdigest())
#     sleep(10)

m = hashlib.sha1()
with open("tests/data/atom_response.json") as f:
    content = f.read()
m.update(content)
conn.put_record(STREAM_NAME,content,partition_key=m.hexdigest())
