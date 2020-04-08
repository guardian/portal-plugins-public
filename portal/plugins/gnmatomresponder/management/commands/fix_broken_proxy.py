from django.conf import settings
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Checks for a broken lowres proxy and rebuilds it if necessary"

    def handle(self, *args, **options):
        from portal.plugins.gnmatomresponder.transcode_check import check_for_broken_proxy, delete_existing_proxy, transcode_proxy
        item_id = args[0]
        if item_id is None:
            print "You must specify the item id to fix as the first and only argument"
            exit(1)

        print "{0}: Checking for broken proxy".format(item_id)

        should_regen, shape_id = check_for_broken_proxy(item_id)

        if should_regen:
            print "{0}: Proxy needs regen. Existing shape id is {1}".format(item_id, shape_id)
            if shape_id is not None:
                print "{0}: Deleting invalid proxy"
                delete_existing_proxy(item_id, shape_id)
            transcode_proxy(item_id, "lowres")
        else:
            print "{0}: Proxy is OK".format(item_id)