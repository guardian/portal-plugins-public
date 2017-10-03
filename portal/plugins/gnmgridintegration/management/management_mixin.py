class ManagementMixin(object):
    """
    Mixin class that provides functionality for install/uninstall commands
    """
    DEFAULT_ITEM_META_FIELDS = {
        'credit': {
            'format_string': "{vs_field_data}",
            'vs_field': 'gnm_master_generic_source'
        },
        'description': {
            'format_string': "Still from frame {frame_number} of '{vs_field_data}'",
            'vs_field': 'gnm_master_website_headline'
        },
    }

    DEFAULT_RIGHTS_META_FIELDS = {
        'category': {
            'format_string': 'screengrab',
        },
        'source': {
            'format_string': "PLUTO Master '{vs_field_data}'",
            'vs_field': 'gnm_master_website_headline'
        }
    }

    CONFIG_STARTING_LINE = "### Grid installation config"
    CONFIG_ENDING_LINE = "### END Grid installation config"
    CONFIG_BLOCK = """
GNM_GRID_API_KEY = {grid_api_key}
GRID_RETRY_DELAY = 5
GRID_MAX_RETRIES = 10
GNM_GRID_DOMAIN = \"media.test.dev-gutools.co.uk\"
"""

    def get_notification_url(self):
        from django.core.urlresolvers import reverse, reverse_lazy
        import socket
        return "http://{host}{path}".format(host=socket.getfqdn(),path=reverse('gridintegration_callback_url'))

    def setup_notification(self):
        from gnmvidispine.vs_notifications import VSNotification, HttpNotification, VSTriggerEntry
        from gnmvidispine.vidispine_api import VSBadRequest
        from django.conf import settings

        #my_notification = HttpNotification(None).new()
        n = VSNotification(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
        my_notification = None
        for act in n.actions:
            my_notification = act
            break

        #my_notification.synchronous = False
        my_notification.retry = 5
        my_notification.contentType = 'application/json'
        my_notification.method = 'POST'
        my_notification.timeout = 30
        my_notification.url = self.get_notification_url()

        my_trigger = VSTriggerEntry(None)
        my_trigger.trigger_class = 'job'
        my_trigger.action = 'stop'
        my_trigger.filter = {'type': 'THUMBNAIL'}


        n.trigger = my_trigger
        n.objectclass = 'job'

        print "Installing notification in vidispine..."
        try:
            n.save()
        except VSBadRequest:
            print n.as_xml()
            raise

        #print n.as_xml()

    def remove_notification(self):
        from gnmvidispine.vs_notifications import VSNotificationCollection
        from django.conf import settings
        import re
        c = VSNotificationCollection(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)

        is_our_job = re.compile(r'portal.plugins.gnmgridintegration/')

        print "Scanning for our notification"
        c.objectclass='job'
        i=0
        for n in c.notifications():
            #print unicode(n)
            try:
                for act in n.actions:
                    url = act.url
                    #print "debug: got url {0} for {1}".format(url,n.name)
                    #if url == self.get_notification_url():
                    if is_our_job.search(url):
                        print "Deleting notification {0}".format(n.name)
                        i+=1
                        n.delete()

            except VSNotificationCollection.UnknownActionType:
                pass
        if i==0:
            print "Warning: Unable to find any notifications to remove"
        else:
            print "Removed {0} relevant notifications".format(i)

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