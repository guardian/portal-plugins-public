__author__ = 'Andy Gallagher <andy.gallagher@theguardian.com>'

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Uninstall the FCS S3-Glacier restore plugin'

    def add_arguments(self, parser):
        pass

    def add_config_lines(self,dest):
        dest.write("""### GNM AWS GR installation config

### END GNM AWS GR installation config
""")

    def remove_group(self, rolename):
        from portal.plugins.gnmawsgr.tasks import make_vidispine_request
        import httplib2

        agent = httplib2.Http()
        make_vidispine_request(agent,"DELETE","/API/group/{groupname}".format(groupname=rolename))

    def handle(self, *args, **options):
        import shutil
        import os
        import sys
        import re

        print "Removing S3-glacier group..."
        self.remove_group('AWS_GR_Restore')
        print "Done."

        installation_path =  os.path.dirname(os.path.realpath(sys.argv[0]))
        print "Installation path is %s" % installation_path

        localsettings = os.path.join(installation_path,'portal','localsettings.py')
        backupfile = localsettings + ".bak"
        shutil.move(localsettings, backupfile)

        print "Backing up {0} to {1}".format(localsettings, backupfile)

        starting_line = re.compile(r'^### GNM AWS GR installation config')
        ending_line = re.compile(r'^### END GNM AWS GR installation config')
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
