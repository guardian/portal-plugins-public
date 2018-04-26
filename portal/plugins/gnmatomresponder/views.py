from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.generic.list import ListView
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


class ImportJobListView(ListView):
    from models import ImportJob
    model = ImportJob

    template_name = "gnmatomresponder/import_job_list.html"

    def get_queryset(self):
        qs = self.model.objects.all()

        if 'status' in self.request.GET:
            qs = qs.filter(status=self.request.GET['status'])
        if 'itemId' in self.request.GET and self.request.GET['itemId']!='':
            qs = qs.filter(item_id=self.request.GET['itemId'])

        return qs.order_by('-completed_at', '-started_at')

    def get_context_data(self, **kwargs):
        rtn = super(ImportJobListView, self).get_context_data(**kwargs)
        if 'intest' in self.request.GET:
            rtn['in_test'] = True
        else:
            rtn['in_test'] = False
        return rtn
