# coding: utf-8
from django.conf import settings
from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
from portal.plugins.kinesisresponder.management.kinesis_responder_basecommand import KinesisResponderBaseCommand


class Command(KinesisResponderBaseCommand):
    stream_name = settings.ATOM_RESPONDER_STREAM_NAME
    role_name = settings.ATOM_RESPONDER_ROLE_NAME

    session_name = "GNMAtomResponder"

    def handle(self, *args, **options):
        from portal.plugins.gnmatomresponder.notification import find_notification, create_notification
        notification_uri = find_notification()
        if notification_uri is None:
            print "Callback notification not present in Vidispine. Installing..."
            create_notification()
            notification_uri = find_notification()
            if notification_uri is None:
                raise RuntimeError("Unable to install notification into Vidispine")
        print "Notification URI is at {0}".format(notification_uri)

        newoptions = options.copy()
        newoptions.update({
            'aws_access_key_id': settings.ATOM_RESPONDER_AWS_KEY_ID,
            'aws_secret_access_key': settings.ATOM_RESPONDER_SECRET
        })

        super(Command, self).handle(*args,**newoptions)

    def startup_thread(self, conn, shardinfo):
        return MasterImportResponder(self.role_name,self.session_name,self.stream_name,shardinfo['ShardId'],
                                     aws_access_key_id=settings.ATOM_RESPONDER_AWS_KEY_ID, aws_secret_access_key=settings.ATOM_RESPONDER_SECRET)