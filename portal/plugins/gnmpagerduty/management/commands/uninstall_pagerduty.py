from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Uninstalls the PagerDuty Celery task'

    def add_arguments(self, parser):
        pass

    def add_config_lines(self,dest):
        dest.write("""### PagerDuty installation config
if not 'CELERY_IMPORTS' in globals():
    CELERY_IMPORTS = []

CELERY_IMPORTS  += ['portal.plugins.gnmpagerduty.tasks']
### END PagerDuty installation config
""")

    def handle(self, *args, **options):
        import shutil
        import os
        import sys
        import re

        installation_path =  os.path.dirname(os.path.realpath(sys.argv[0]))
        print "Installation path is %s" % installation_path

        localsettings = os.path.join(installation_path,'portal','localsettings.py')
        backupfile = localsettings + ".bak"
        shutil.move(localsettings, backupfile)

        print "Backing up {0} to {1}".format(localsettings, backupfile)

        starting_line = re.compile(r'^### PagerDuty installation config')
        ending_line = re.compile(r'^### END PagerDuty installation config')
        try:
            with open(backupfile,mode='r') as source:
                with open(localsettings,mode='w') as dest:
                    in_block = False
                    block_found = False
                    for lines in source:
                        if not in_block:
                            if starting_line.match(lines):
                                in_block = True
                                block_found = True
                                print "Existing configuration found"
                            else:
                                dest.write(lines)
                        else:
                            #swallow all in-block lines
                            if ending_line.match(lines):
                                print "Removing existing configuration"
                                in_block = False

                    if not block_found:
                        print "No configuration found in %s" % localsettings

            print "Configuration finished.  You now need to restart Portal and the Celery services by running sudo supervisorctl restart all"
        except StandardError as e:
            print "An error occurred: {0}".format(str(e))
            print "Restoring backup of old settings file..."
            shutil.move(backupfile, localsettings)
            print "Restore done.  Original error was:"
            raise

