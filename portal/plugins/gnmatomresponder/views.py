from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.generic.list import ListView
from django.http import HttpResponse
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
        from models import ImportJob
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

        try:
            process_notification(notification)
            return Response({'status': 'ok'})
        except ImportJob.DoesNotExist:
            logger.error("JobNotifyView: No import job found for {0}".format(notification))
            return Response({'status': 'notfound'}, status=200)


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


class ResyncToAtomApi(APIView):
    renderer_classes = (JSONRenderer, )
    authentication_classes = (IsAuthenticated, )

    def get(self, request, item_id=None):
        from portal.plugins.gnm_masters.models import VSMaster
        import portal.plugins.gnm_vidispine_utils.constants as const
        import requests
        from django.conf import settings

        try:
            master = VSMaster(item_id, request.user)
            atom_id = master.get(const.GNM_MASTERS_MEDIAATOM_ATOMID, "")

            if atom_id is None:
                return Response({"status": "error","error": "This master has no atom ID yet"}, status=400)

            url = settings.GNM_ATOM_RESPONDER_LAUNCHDETECTOR_URL + "/update/" + atom_id
            logger.info("Update URL for {0} is {1}".format(item_id, url))
            response = requests.put(url)

            logger.info("Updating {0}: Launch detector said {1} {2}".format(item_id, response.status_code, response.content))
            #simply echo the Launch Detector's response back to the client
            return Response(response.json(), status=response.status_code)
        except requests.ConnectTimeout:
            return Response({"status": "error", "error": "Timeout connecting to LaunchDetector, please try again and notify multimediatech@theguardian.com"},status=500)
        except requests.ConnectionError:
            return Response({"status": "error", "error": "Unable to connect to LaunchDetector, please notify multimediatech@theguardian.com"},status=500)
        except Exception as e:
            return Response({"status": "error", "error": str(e)},status=500)