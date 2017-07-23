from __future__ import absolute_import
from os import environ
import unittest2
import os.path
environ["DJANGO_SETTINGS_MODULE"] = "gnmlibrarytool.tests.django_test_settings"
environ["CI"] = "True"  #simulate a CI environment even if we're not in one, this will stop trying to import portal-specific stuff
#which breaks the tests
import django.test


class TestPluginTemplates(django.test.TestCase):
    def _dorender(self, templatename, context):
        from django.template import loader

        mydir = os.path.dirname(os.path.abspath(__file__))
        templatedir = os.path.abspath(os.path.join(mydir, '..','templates','gnmlibrarytool'))

        return loader.render_to_string(os.path.join(templatedir, templatename),context)

    def test_mediaview_storagerules(self):
        rendered_content = self._dorender("mediaview_storagerules.html",{'item_id': 'VX-1234', 'rules': []})
        self.assertIn('<input type="hidden" name="itemid" value="VX-1234">', rendered_content)

    def test_mediaview_menuitem(self):
        rendered_content = self._dorender("mediaviewmenuitem.html",{'item_id': 'VX-1234'})
        self.assertIn('{"func": "load_storage_rule_info", "args": ["","VX-1234"]} }', rendered_content)

    def test_nav(self):
        rendered_content = self._dorender("nav.html",{})
        self.assertIn('<a href="/gnmlibrarytool/">Library Manager Tool</a>', rendered_content)
        self.assertIn('<a href="/gnmlibrarytool/rule/list/">Edit Storage Rules</a>', rendered_content)

    def test_navigation(self):
        rendered_content = self._dorender("nav.html",{})
        self.assertIn('<a href="/gnmlibrarytool/">Library Manager Tool</a>', rendered_content)
        self.assertIn('<a href="/gnmlibrarytool/rule/list/">Edit Storage Rules</a>', rendered_content)

