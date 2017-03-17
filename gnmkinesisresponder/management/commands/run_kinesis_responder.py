# coding: utf-8
from django.core.management.base import BaseCommand
import os
from boto import kinesis
from portal.plugins.gnmkinesisresponder.kinesis_responder import KinesisResponder
from pprint import pprint
from time import sleep

STREAM_NAME='TestContentAtom2'


class Command(BaseCommand):
    args = ''
    help = 'runs the test kinesis responder'

    def handle(self, *args, **options):
        conn = kinesis.connect_to_region('eu-west-1')

        streaminfo = conn.describe_stream(STREAM_NAME)

        pprint(streaminfo)

        threadlist = map(lambda shardinfo: KinesisResponder(conn,STREAM_NAME,shardinfo['ShardId']), streaminfo['StreamDescription']['Shards'])

        print "Stream {0} has {1} shards".format(STREAM_NAME,len(threadlist))

        for t in threadlist:
            t.daemon = True
            t.start()

        #simplest way to allow ctrl-C when dealing with threads
        try:
            while True:
                sleep(3600)
        except KeyboardInterrupt:
            print "CTRL-C caught, cleaning up"

        # r = KinesisResponder(conn,STREAM_NAME,SHARD_NAME)
        # print "Running kinesis responder..."
        # r.run()
