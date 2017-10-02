from django.conf import settings
import logging
import traceback

logger = logging.getLogger(__name__)


def inform_sentry_exception(extra_ctx={}):
    if not hasattr(settings,"RAVEN_CONFIG"): #don't bother if we are not set up for it
        return

    try:
        import raven

        ravenClient = raven.Client(dsn=settings.RAVEN_CONFIG['dsn'])
        ravenClient.extra_context(extra_ctx)
        ravenClient.captureException()
    except Exception as e:
        logger.error("Unable to send to Sentry: {0}".format(str(e)))
        logger.error(traceback.format_exc())


def inform_sentry(message, extra_ctx={}):
    if not hasattr(settings,"RAVEN_CONFIG"): #don't bother if we are not set up for it
        return

    try:
        import raven

        ravenClient = raven.Client(dsn=settings.RAVEN_CONFIG['dsn'])
        ravenClient.extra_context(extra_ctx)
        ravenClient.captureMessage(message)
    except Exception as e:
        logger.error("Unable to send to Sentry: {0}".format(str(e)))
        logger.error(traceback.format_exc())