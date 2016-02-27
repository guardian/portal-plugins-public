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

    def get_notification_url(self):
        from django.core.urlresolvers import reverse, reverse_lazy
        import socket
        return "http://{host}{path}".format(host=socket.getfqdn(),path=reverse('gridintegration_callback_url'))

    def setup_notification(self):
        from vidispine.vs_notifications import VSNotification, HttpNotification, VSTriggerEntry
        from vidispine.vidispine_api import VSBadRequest
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

        print "Installing notification in Vidispine..."
        try:
            n.save()
        except VSBadRequest:
            print n.as_xml()
            raise

        #print n.as_xml()

    def remove_notification(self):
        from vidispine.vs_notifications import VSNotificationCollection
        from django.conf import settings
        import re
        c = VSNotificationCollection(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)

        is_our_job = re.compile(r'gnmgridintegration/')

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
