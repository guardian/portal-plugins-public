# coding: utf-8
from django.conf import settings
from portal.plugins.gnmatomresponder.master_importer import MasterImportResponder
from portal.plugins.kinesisresponder.management.kinesis_responder_basecommand import KinesisResponderBaseCommand
import logging

logger = logging.getLogger(__name__)


class Command(KinesisResponderBaseCommand):
    stream_name = settings.ATOM_RESPONDER_STREAM_NAME
    role_name = settings.ATOM_RESPONDER_ROLE_NAME

    session_name = "GNMAtomResponder"

    def handle(self, *args, **options):
        from portal.plugins.gnmatomresponder.notification import find_notification, create_notification
        from portal.plugins.kinesisresponder.sentry import inform_sentry_exception
        import traceback
        import xml.etree.cElementTree as ET
        from gnmvidispine.vs_external_id import ExternalIdNamespace
        from gnmvidispine.vidispine_api import VSNotFound

        notification_uri = find_notification()
        if notification_uri is None:
            logger.info("Callback notification not present in Vidispine. Installing...")
            create_notification()
            notification_uri = find_notification()
            if notification_uri is None:
                raise RuntimeError("Unable to install notification into Vidispine")
        logger.info("Notification URI is at {0}".format(notification_uri))

        #ensure that the namespace for our external IDs is present. If not, create it.
        #this is to make it simple for LaunchDetector to look up items by atom ID
        extid_namespace = ExternalIdNamespace(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
        try:
            extid_namespace.populate("atom_uuid")
            logger.info("Found external id namespace atom_uuid")
        except VSNotFound:
            try:
                extid_namespace.create("atom_uuid","[A-Fa-f0-9]{8}\-[A-Fa-f0-9]{4}\-[A-Fa-f0-9]{4}\-[A-Fa-f0-9]{4}\-[A-Fa-f0-9]{12}")
                logger.info("Created new external id namespace atom_uuid")
            except Exception as e:
                logger.error(traceback.format_exc())
                inform_sentry_exception(extra_ctx={'namespace_source': ET.tostring(extid_namespace._xmldoc, encoding="UTF-8")})
                raise

        newoptions = options.copy()
        newoptions.update({
            'aws_access_key_id': settings.ATOM_RESPONDER_AWS_KEY_ID,
            'aws_secret_access_key': settings.ATOM_RESPONDER_SECRET
        })

        super(Command, self).handle(*args,**newoptions)

    def startup_thread(self, conn, shardinfo):
        return MasterImportResponder(self.role_name,self.session_name,self.stream_name,shardinfo['ShardId'],
                                     aws_access_key_id=settings.ATOM_RESPONDER_AWS_KEY_ID,
                                     aws_secret_access_key=settings.ATOM_RESPONDER_SECRET)