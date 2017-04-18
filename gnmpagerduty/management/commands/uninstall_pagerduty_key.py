from django.core.management.base import BaseCommand
from portal.plugins.gnmpagerduty.management.management_mixin import ManagementMixin


class Command(ManagementMixin, BaseCommand):
    help = 'Removes the PagerDuty key'

    def handle(self, *args, **options):
        self.update_config_file({}, remove=True)