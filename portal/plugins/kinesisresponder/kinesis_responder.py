from boto import kinesis
from boto.kinesis import exceptions, layer1 as kl1
import boto.exception
from boto import sts
from models import KinesisTracker
from datetime import datetime, timedelta
import logging
from time import sleep
from threading import Thread
import traceback
logger = logging.getLogger(__name__)

TRIM_HORIZON = 'TRIM_HORIZON'
AFTER_SEQUENCE_NUMBER = 'AFTER_SEQUENCE_NUMBER'


class KinesisResponder(Thread):
    """
    Kinesis responder class that deals with getting stuff from a stream shard.  You can subclass this to do interesting
    things with the messages - simply over-ride the process() method to get called whenever something comes in from the stream.
    """
    def __init__(self, role_name, session_name, stream_name, shard_id, *args,**kwargs):
        """
        Initialise
        :param credentials: AWS connection credentials object from boto
        :param stream_name: The name, not ARN, of the stream
        :param shard_id: Shard to connect to
        """
        super(KinesisResponder, self).__init__(*args,**kwargs)
        self.role_name = role_name
        self.session_name = session_name
        self._conn = None
        self.stream_name = stream_name
        self.shard_id = shard_id

        self.refresh_access_credentials()

    def refresh_access_credentials(self):
        sts_conn = sts.connect_to_region('eu-west-1')
        credentials = sts_conn.assume_role(self.role_name, self.session_name)
        self._conn = kinesis.connect_to_region('eu-west-1', aws_access_key_id=credentials.credentials.access_key,
                                               aws_secret_access_key=credentials.credentials.secret_key,
                                               security_token=credentials.credentials.session_token)

    def most_recent_message_id(self):
        """
        Scans the data model to find the most recent message ID, where we want to resume processing from
        :return: String of the sequence number or None of nothing was found
        """
        try:
            record = KinesisTracker.objects.filter(stream_name=self.stream_name).filter(shard_id=self.shard_id).order_by('-created')[0]
            return record.sequence_number

        except IndexError:
            logger.warning("No tracked messages in database yet?")
            return None

    def new_shard_iterator(self):
        """
        Return a shard iterator either pointing to just after the last message we processed (based on our data model)
        or the earliest available point in the stream if no message is available
        :return: Shard iterator
        """
        last_seq_number = self.most_recent_message_id()

        if last_seq_number is None or last_seq_number=='':
            rtn= self._conn.get_shard_iterator(self.stream_name,self.shard_id,TRIM_HORIZON)
            return rtn['ShardIterator']
        else:
            rtn= self._conn.get_shard_iterator(self.stream_name,self.shard_id,AFTER_SEQUENCE_NUMBER,starting_sequence_number=last_seq_number)
            return rtn['ShardIterator']

    def process(self,record, approx_arrival):
        """
        Do something interesting with the data.  Subclass this method to do something useful
        :param record: String of the record content from the stream
        :param approx_arrival: datetime object of the approximate time that this message was put to the stream
        :return: None
        """
        from pprint import pprint
        import json
        print "----------------------------------------------------------"
        print "Message posted at approximately: " + str(approx_arrival)
        pprint(json.loads(record))

    def run(self):
        """
        Main loop for processing the stream
        :return:
        """
        from pprint import pprint
        sleep_delay = 1

        print "Starting up responder thread for shard {0}".format(self.shard_id)
        iterator = self.new_shard_iterator()
        print "shard iterator is {0}".format(iterator)
        while iterator is not None:
            try:
                record = self._conn.get_records(iterator,limit=10)
                if sleep_delay>1:
                    sleep_delay /= 2
            except kinesis.exceptions.ProvisionedThroughputExceededException:
                sleep(sleep_delay)
                sleep_delay*=2
                continue
            except boto.exception.JSONResponseError as e:
                if e.error_code=='ExpiredTokenException':
                    logging.warning("Access credentials expired, refreshing...")
                    self.refresh_access_credentials()
                continue

            time_lag = timedelta(seconds=record['MillisBehindLatest']/1000)
            print "Time lag to this record set is {0}".format(time_lag)
            print "Record set is dated {0}".format(datetime.now() - time_lag)

            pprint(record)
            for rec in record['Records']:
                dbrec = KinesisTracker()
                dbrec.stream_name = self.stream_name
                dbrec.shard_id = self.shard_id
                dbrec.created = datetime.now()
                dbrec.updated = datetime.now()
                dbrec.sequence_number = rec['SequenceNumber']
                dbrec.status = KinesisTracker.ST_SEEN
                dbrec.processing_host = "myhost"
                dbrec.millis_behind_latest = record['MillisBehindLatest']
                dbrec.save()

                dbrec.status = KinesisTracker.ST_PROCESSING
                dbrec.save()
                try:
                    self.process(rec['Data'], datetime.fromtimestamp(rec['ApproximateArrivalTimestamp']))
                    dbrec.status = KinesisTracker.ST_DONE
                    dbrec.save()
                except Exception as e:
                    #FIXME: put a call to Raven here too
                    traceback.print_exc()
                    print str(e)
                    dbrec.status = KinesisTracker.ST_ERROR
                    dbrec.last_exception = str(e)
                    dbrec.exception_trace = traceback.format_exc()
                    dbrec.save()

            iterator = record['NextShardIterator']
            if len(record['Records'])==0 and record['MillisBehindLatest']==0:
                sleep(10)
        logger.info("Ran out of shard records to read")