from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class JobNotifyView(APIView):
    permission_classes = (AllowAny, )
    renderer_classes = (JSONRenderer, )

    def post(self, request):
        """
        Receives notifications from VS that a relevant import has taken place.
        Notification is set up in notification.py
        :param request: Django request object
        :return: Response
        """
        from job_notification import JobNotification
        from lxml.etree import XMLSyntaxError, LxmlError
        from notification import process_notification
        import traceback

        logger.info("Received import notification")
        try:
            notification = JobNotification(request.body)
        except XMLSyntaxError:
            logger.error("Invalid XML document received from Vidispine: {0}".format(request.body))
            return Response({'status': 'Bad XML'}, status=400) #returning 400=> VS won't try again
        except LxmlError:
            logger.error("Unable to process Vidispine XML document, but syntax as ok")
            return Response({'status': 'Unable to process'}, status=500) #returning 500=> VS will try again (more likely problem is our side)

        process_notification(notification)

        return Response({'status': 'ok'})