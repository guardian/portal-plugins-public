from boto import kinesis
from boto.kinesis import exceptions, layer1 as kl1
from models import KinesisTracker
from datetime import datetime, timedelta
import logging
from time import sleep
logger = logging.getLogger(__name__)

TRIM_HORIZON = 'TRIM_HORIZON'
AFTER_SEQUENCE_NUMBER = 'AFTER_SEQUENCE_NUMBER'

class KinesisResponder(object):
    def __init__(self, conn, stream_name, shard_id):
        if not isinstance(conn,kl1.KinesisConnection): raise TypeError

        self._conn = conn
        self.stream_name = stream_name
        self.shard_id = shard_id

    def most_recent_message_id(self):
        try:
            record = KinesisTracker.objects.all().order_by('-created')[0]
            return record.sequence_number

        except IndexError:
            logger.warning("No tracked messages in database yet?")
            return None

    def new_shard_iterator(self):
        last_seq_number = self.most_recent_message_id()

        if last_seq_number is None or last_seq_number=='':
            rtn= self._conn.get_shard_iterator(self.stream_name,self.shard_id,TRIM_HORIZON)
            return rtn['ShardIterator']
        else:
            rtn= self._conn.get_shard_iterator(self.stream_name,self.shard_id,AFTER_SEQUENCE_NUMBER,starting_sequence_number=last_seq_number)
            return rtn['ShardIterator']

    def process(self,record):
        from pprint import pprint
        print "----------------------------------------------------------"
        pprint(record)

    def run(self):
        from pprint import pprint
        sleep_delay = 1
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

            time_lag = timedelta(seconds=record['MillisBehindLatest']/1000)
            print "Time lag to this record set is {0}".format(time_lag)
            print "Record set is dated {0}".format(datetime.now() - time_lag)

            pprint(record)
            for rec in record['Records']:
                dbrec = KinesisTracker()
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
                self.process(rec['Data'])

                dbrec.status = KinesisTracker.ST_DONE
                dbrec.save()

            iterator = record['NextShardIterator']
            if len(record['Records'])==0 and record['MillisBehindLatest']==0:
                sleep(10)
        logger.info("Ran out of shard records to read")