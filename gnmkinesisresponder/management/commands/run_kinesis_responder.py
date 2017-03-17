# coding: utf-8
from django.core.management.base import BaseCommand
import os
from boto import kinesis
from portal.plugins.gnmkinesisresponder.kinesis_responder import KinesisResponder

STREAM_NAME='TestContentAtom2'
SHARD_NAME='shardId-000000000000'


class Command(BaseCommand):
    args = ''
    help = 'runs the test kinesis responder'

    def handle(self, *args, **options):
        conn = kinesis.connect_to_region('eu-west-1')

        r = KinesisResponder(conn,STREAM_NAME,SHARD_NAME)
        print "Running kinesis responder..."
        r.run()
