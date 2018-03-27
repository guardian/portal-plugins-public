from django.conf import settings
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Request a resend of the specific atom ID. This will cause a new version to be created in pluto."

    def handle(self, *args, **options):
        from portal.plugins.gnmatomresponder.media_atom import request_atom_resend

        if len(args)!=1:
            print "ERROR: You must specify an atom ID as the only commandline argument"
            exit(1)

        #this will raise if it fails, and the user will see the error
        request_atom_resend(args[0], settings.ATOM_TOOL_HOST, settings.ATOM_TOOL_SECRET)
        print "Resend request to {0} successful".format(settings.ATOM_TOOL_HOST)