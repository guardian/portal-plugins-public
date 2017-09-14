# coding: utf-8
from django.core.management.base import BaseCommand
import os
from boto import kinesis, sts
from pprint import pprint
from time import sleep


class KinesisResponderBaseCommand(BaseCommand):
    """
    Base class for a Django command to run the responder.  Subclass this and:
     - set stream_name, role_name and session_name attributes
     - override startup_thread to provide an instance of your responder
    """
    args = ''
    help = 'runs the test kinesis responder'

    stream_name = 'stream name to connect to'
    role_name = 'ARN of role to use'
    session_name = 'session_name'

    def startup_thread(self, conn, shardinfo):
        """
        Override this method to start up a processing thread. This is called once for every shard in the stream
        :param conn: kinesis connection object
        :param shardinfo: dictionary of information about the shard, returned from describe_stream
        :return: a KinesisResponser subclass instance that will handle the messages for this shard
        """
        raise RuntimeError("startup_thread must be implemented in your subclass!")

    def handle(self, *args, **options):
        sts_conn = sts.connect_to_region('eu-west-1')
        credentials = sts_conn.assume_role(self.role_name, self.session_name)
        pprint(credentials.credentials.__dict__)

        conn = kinesis.connect_to_region('eu-west-1', aws_access_key_id=credentials.credentials.access_key,
                                         aws_secret_access_key=credentials.credentials.secret_key,
                                         security_token=credentials.credentials.session_token)

        streaminfo = conn.describe_stream(self.stream_name)

        pprint(streaminfo)

        threadlist = map(lambda shardinfo: self.startup_thread(conn, shardinfo), streaminfo['StreamDescription']['Shards'])

        print "Stream {0} has {1} shards".format(self.stream_name,len(threadlist))

        for t in threadlist:
            t.daemon = True
            t.start()

        print "Started up and processing. Hit CTRL-C to stop."
        #simplest way to allow ctrl-C when dealing with threads
        try:
            while True:
                sleep(3600)
        except KeyboardInterrupt:
            print "CTRL-C caught, cleaning up"
