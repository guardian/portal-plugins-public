__author__ = 'Andy Gallagher <andy.gallagher@theguardian.com>'

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Grabs a bunch of data to test the profiler with'

    max_items=20

    def add_arguments(self, parser):
        parser.add_argument('--items',dest='maxitems')

    def handle(self, *args, **options):
        from gnmvidispine.vs_search import VSItemSearch
        from django.conf import settings
        from portal.plugins.gnmuploadprofiler.models import OutputTimings
        from portal.plugins.gnmuploadprofiler.tasks import profile_item

        max_items = self.max_items
        if 'maxitems' in options:
            max_items=int(options.maxitems)

        n=1

        s=VSItemSearch(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,user=settings.VIDISPINE_USERNAME,
                       passwd=settings.VIDISPINE_PASSWORD)

        s.addCriterion({'gnm_master_generic_status': 'Published'})

        result = s.execute()

        for item in result.results(shouldPopulate=False):
            print "{0}: Checking {1}...".format(n, item.name),
            try:
                record = OutputTimings.objects.get(item_id=item.name)
                print "already done."
            except OutputTimings.DoesNotExist:
                print "requesting profile"
                profile_item.delay(item.name)
                n += 1

            if n>=max_items:
                break