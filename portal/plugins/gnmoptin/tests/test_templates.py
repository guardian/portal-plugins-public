from __future__ import absolute_import
import os.path
import django.test


class TestTemplates(django.test.TestCase):
    def _dorender(self, templatename, context):
        from django.template import loader

        mydir = os.path.dirname(os.path.abspath(__file__))
        templatedir = os.path.abspath(os.path.join(mydir, '..','templates','gnmoptin'))

        loader.add_to_builtins('portal.plugins.gnmoptin.tests.loader_tags')

        return loader.render_to_string(os.path.join(templatedir, templatename),context)

    def test_my_optins(self):
        rendered_content = self._dorender("my_optins.html",{})
        self.assertIn('<li>You have not enabled any optional features at the moment.  Why not <a href=', rendered_content)

    def test_add_optins(self):
        rendered_content = self._dorender("add_optins.html",{})
        self.assertIn('<form action="" method="post">', rendered_content)
        self.assertIn('<input type="submit" value="Save" />', rendered_content)

    def test_change_optins(self):
        rendered_content = self._dorender("change_optins.html",{})
        self.assertIn('<form action="" method="post">', rendered_content)
        self.assertIn('<label for="">Feature:</label>', rendered_content)
        self.assertIn('<input type="submit" value="Save" />', rendered_content)

    def test_delete_optins(self):
        rendered_content = self._dorender("delete_optins.html",{})
        self.assertIn('<form action="" method="post">', rendered_content)
        self.assertIn('<p>Are you sure you want to opt out of ""?</p>', rendered_content)
        self.assertIn('<input type="submit" value="Confirm" />', rendered_content)

    def test_user_profile_menu(self):
        rendered_content = self._dorender("user_profile_menu.html",{})
        self.assertIn('<span class="iicon" style="background-position:-197px -334px"></span>My Opt-Ins</a>', rendered_content)
