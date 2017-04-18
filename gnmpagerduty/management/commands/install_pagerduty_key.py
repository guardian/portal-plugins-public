from django.core.management.base import BaseCommand
from optparse import make_option
from portal.plugins.gnmpagerduty.management.management_mixin import ManagementMixin
import logging

logger = logging.getLogger('portal.plugins.gnmpagerduty.installer')


class Command(ManagementMixin, BaseCommand):
    help = 'Installs the PagerDuty key'
    option_list = BaseCommand.option_list + (
        make_option('--key',dest='api_key', help='API key for PagerDuty'),
    )

    def handle(self, *args, **options):
        if options['api_key'] is None or len(options['api_key'])==0:
            logger.error("You must specify and API key when installing by using the --key option")
            print "You must specify an API key when installing by using the --key option"
            exit(2)

        logger.info("Setting API key....")
        self.update_config_file({'pd_api_key': "'" + options['api_key'] + "'"})
        logger.info("Done")

        logger.info("Installer completed")