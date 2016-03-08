from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from portal.plugins.gnmgridintegration.management.management_mixin import ManagementMixin
import logging

logger = logging.getLogger('portal.plugins.gnmgridintegration.installer')

class Command(ManagementMixin, BaseCommand):
    help = 'Installs the Grid integrator plugin'
    option_list = BaseCommand.option_list + (
        make_option('--key',dest='api_key', help='API key to communicate with the Grid'),
    )

    def handle(self, *args, **options):
        from portal.plugins.gnmgridintegration.models import GridMetadataFields
        from gnmvidispine.vs_field import VSField, VSNotFound
        from django.conf import settings
        from portal.plugins.gnmgridintegration.notification_handler import VIDISPINE_GRID_REF_FIELD
        from pprint import pprint

        if options['api_key'] is None or len(options['api_key'])==0:
            logger.error("You must specify and API key when installing by using the --key option")
            print "You must specify an API key when installing by using the --key option"
            exit(2)

        logger.info("Setting API key....")
        self.update_config_file({'grid_api_key': "'" + options['api_key'] + "'"})
        logger.info("Done")

        logger.info("Configuring notification...")
        self.setup_notification()
        fieldref = VSField(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                           user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
        logger.info("Checking fields exist...")
        try:
            fieldref.populate(VIDISPINE_GRID_REF_FIELD)
            #print "Found field {0} in existence".format(VIDISPINE_GRID_REF_FIELD)
            logger.info("Found field {0} in existence".format(VIDISPINE_GRID_REF_FIELD))
        except VSNotFound as e:
            #print "Field {0} does not exist.  Attempting to create...".format(VIDISPINE_GRID_REF_FIELD)
            logger.info("Field {0} does not exist.  Attempting to create...".format(VIDISPINE_GRID_REF_FIELD))
            fieldref.create(VIDISPINE_GRID_REF_FIELD,'string-exact',commit=True)

        logger.info("Checking that metadata options are in place....")
        if len(GridMetadataFields.objects.all())==0:
            logger.info("No metadata options set.  Installing defaults...")
            for k,v in self.DEFAULT_ITEM_META_FIELDS.items():
                f = GridMetadataFields()
                f.grid_field_name = k
                f.format_string = v['format_string']
                if 'vs_field' in v:
                    f.vs_field = v['vs_field']
                f.type = 1
                f.save()
            for k,v in self.DEFAULT_RIGHTS_META_FIELDS.items():
                f = GridMetadataFields()
                f.grid_field_name = k
                f.format_string = v['format_string']
                if 'vs_field' in v:
                    f.vs_field = v['vs_field']
                f.type = 2
                f.save()
            logger.info("Saved default metadata options.")

        logger.info("Installer completed")