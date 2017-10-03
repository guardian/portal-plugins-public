# coding: utf-8
from django.conf import settings
from portal.plugins.kinesisresponder.management.kinesis_responder_basecommand import KinesisResponderBaseCommand
from portal.plugins.kinesisresponder.kinesis_responder import KinesisResponder
import logging

logger = logging.getLogger(__name__)


class Command(KinesisResponderBaseCommand):
    stream_name = settings.ATOM_RESPONDER_STREAM_NAME
    role_name = settings.ATOM_RESPONDER_ROLE_NAME

    session_name = "show_kinesis_stream"

    def handle(self, *args, **options):
        newoptions = options.copy()
        newoptions.update({
            'aws_access_key_id': settings.ATOM_RESPONDER_AWS_KEY_ID,
            'aws_secret_access_key': settings.ATOM_RESPONDER_SECRET
        })

        super(Command, self).handle(*args,**newoptions)

    def startup_thread(self, conn, shardinfo):
        return KinesisResponder(self.role_name,self.session_name,self.stream_name,shardinfo['ShardId'],
                                aws_access_key_id=settings.ATOM_RESPONDER_AWS_KEY_ID,
                                aws_secret_access_key=settings.ATOM_RESPONDER_SECRET,
                                should_save=False
                                )