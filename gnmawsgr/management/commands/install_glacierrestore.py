__author__ = 'Andy Gallagher <andy.gallagher@theguardian.com>'

from django.core.management.base import BaseCommand, CommandError
from portal.plugins.gnmawsgr.vsmixin import VSMixin


class Command(VSMixin, BaseCommand):
    help = 'Installs the FCS S3-Glacier Restore plugin'

    def add_arguments(self, parser):
        pass

    def add_config_lines(self,dest):
        dest.write("""### GNM AWS GR installation config

### END GNM AWS GR installation config
""")

    def _field_extra_data_node(self, doc):
        for dataNode in doc.findall('{0}data'.format(self._ns)):
            keyNode = dataNode.find('{0}key'.format(self._ns))
            if keyNode.text == 'extradata':
                valNode = dataNode.find('{0}value'.format(self._ns))
                return valNode
        return None

    def _field_extra_data(self, doc):
        import json
        n = self._field_extra_data_node(doc)
        return json.loads(n.text)

    def _update_extra_data(self,doc,newval):
        import json
        n = self._field_extra_data_node(doc)
        n.text = json.dumps(newval)

    def add_choices_to_field(self, fieldname, choices):
        import httplib2
        import xml.etree.cElementTree as ET
        from pprint import pprint

        h=httplib2.Http()
        headers, content = self._make_vidispine_request(h,"GET","/API/metadata-field/{0}?data=all".format(fieldname),
                                                        body=None,headers={'Accept': 'application/xml'})
        rootEl = ET.fromstring(content)
        extra_data = self._field_extra_data(rootEl)

        #pprint(extra_data)
        if not isinstance(choices,list):
            choices = [choices]

        for c in choices:
            if isinstance(c,tuple):
                extra_data['values'].append({u'key': unicode(c[0]), u'value': unicode(c[1])})
            else:
                extra_data['values'].append({u'key': unicode(c), u'value': unicode(c)})
        #pprint(extra_data)

        self._update_extra_data(rootEl,extra_data)
        #print ET.tostring(rootEl)

        headers, content = self._make_vidispine_request(h,"PUT","/API/metadata-field/{0}".format(fieldname),
                                                        body=ET.tostring(rootEl),headers={})


    def make_group(self, groupname, groupdesc=None):
        from xml.etree.ElementTree import Element,SubElement,tostring
        from portal.plugins.gnmawsgr.tasks import make_vidispine_request,HttpError
        import httplib2

        agent = httplib2.Http()

        root_el = Element('GroupDocument',attrib={'xmlns': 'http://xml.vidispine.com/schema/vidispine'})
        name_el = SubElement(root_el, 'groupName')
        name_el.text = groupname

        #print tostring(root_el)
        try:
            make_vidispine_request(agent,"PUT","/API/group/{groupname}".format(groupname=groupname),tostring(root_el),
                               {'Accept': 'application/json'})
        except HttpError as e:
            if e.code == 409: #conflicterror=>group already exists
                print "Group {0} already exists".format(groupname)
            else:
                raise

        if groupdesc is not None:
            make_vidispine_request(agent,"PUT","/API/group/{groupname}/description".format(groupname=groupname),unicode(groupdesc),
                                   {'Accept': 'application/json'},content_type='text/plain')

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

        print "Ensuring that asset status values are present"
        self.add_choices_to_field('gnm_asset_status', ['Waiting for Archive Restore'])
        print "Done"

        print "Installing glacier restore role..."
        self.make_group('AWS_GR_Restore',"Add users to this group to allow them to use the S3-Glacier restore plugin")
        print "Done."
        exit(1)

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
                            #swallow all in-block lines then replace them
                            if ending_line.match(lines):
                                print "Over-writing existing configuration with current version"
                                self.add_config_lines(dest)
                                in_block = False

                    if not block_found:
                        print "No configuration found, adding config to %s" % localsettings
                        self.add_config_lines(dest)
            print "Configuration finished.  You now need to restart Portal and the Celery services by running sudo supervisorctl restart all"
        except StandardError as e:
            print "An error occurred: {0}".format(str(e))
            print "Restoring backup of old settings file..."
            shutil.move(backupfile, localsettings)
            print "Restore done.  Original error was:"
            raise
