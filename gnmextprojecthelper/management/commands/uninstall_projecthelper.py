from django.core.management.base import BaseCommand, CommandError
from portal.plugins.gnmextprojecthelper.management.management_mixin import ManagementMixin

class Command(ManagementMixin, BaseCommand):
    help = 'Removes the GNM external project helper plugin'

    def handle(self, *args, **options):
        self.update_config_file({}, remove=True)