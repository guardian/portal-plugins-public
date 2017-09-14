# coding: utf-8
from portal.plugins.kinesisresponder.management.commands.kinesis_responder_basecommand import KinesisResponderBaseCommand
from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
from django.conf import settings


class Command(KinesisResponderBaseCommand):
    stream_name = settings.ATOM_RESPONDER_STREAM_NAME
    role_name = settings.ATOM_RESPONDER_ROLE_NAME

    session_name = "GNMAtomResponder"

    def startup_thread(self, conn, shardinfo):
        return MasterImportResponder(conn,self.stream_name,shardinfo['ShardId'])