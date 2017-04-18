class ManagementMixin(object):
    """
    Mixin class that provides functionality for install/uninstall commands
    """

    CONFIG_STARTING_LINE = "### PagerDuty key config"
    CONFIG_ENDING_LINE = "### END PagerDuty key config"
    CONFIG_BLOCK = """
PAGERDUTY_KEY = {pd_api_key}
"""

    def add_config_lines(self,dest,params):
        dest.write(self.CONFIG_STARTING_LINE)
        dest.write("\n")
        dest.write(self.CONFIG_BLOCK.format(**params))
        if not self.CONFIG_BLOCK.endswith("\n"):
            dest.write("\n")
        dest.write(self.CONFIG_ENDING_LINE)
        dest.write("\n")

    def update_config_file(self,params, remove=False):
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

        starting_line = re.compile(r'^{0}'.format(self.CONFIG_STARTING_LINE))
        ending_line = re.compile(r'^{0}'.format(self.CONFIG_ENDING_LINE))
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
                            #swallow all in-block lines then replace them
                            if ending_line.match(lines):
                                if remove:
                                    print "Removing existing configuration"
                                    pass
                                else:
                                    print "Over-writing existing configuration with current version"
                                    self.add_config_lines(dest,params)
                                in_block = False

                    if not block_found:
                        print "No configuration found, adding config to %s" % localsettings
                        self.add_config_lines(dest,params)
            print "Configuration finished.  You now need to restart Portal and the Celery services by running sudo supervisorctl restart all"
        except StandardError as e:
            print "An error occurred: {0}".format(str(e))
            print "Restoring backup of old settings file..."
            shutil.move(backupfile, localsettings)
            print "Restore done.  Original error was:"
            raise