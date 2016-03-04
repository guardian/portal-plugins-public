from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from portal.plugins.gnmextprojecthelper.management.management_mixin import ManagementMixin
import logging

logger = logging.getLogger('portal.plugins.gnmgridintegration.installer')


class Command(ManagementMixin, BaseCommand):
    help = 'Installs the GNM external project helper plugin'

    def handle(self, *args, **options):
        logger.info("Installing initial configuration")
        self.update_config_file({})
        logger.info("Installer completed")