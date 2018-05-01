# -*- coding: utf-8 -*-
import django.test
from datetime import datetime


class TestImportJob(django.test.TestCase):
    fixtures = [
        "ImportJobs"
    ]

    def test_to_unicode(self):
        """
        check that importjob model can handle unicode characters in string repr
        :return:
        """
        from portal.plugins.gnmatomresponder.models import ImportJob

        j = ImportJob(item_id="VX-123", job_id="VX-456", status="Started", started_at=datetime.now(),
                      atom_title=u"€ symbol is for utf")

        j.save()
        self.assertEqual(unicode(j), u"Import of € symbol is for utf from Unknown user to item VX-123")
        self.assertEqual(str(j),"Import of \u20ac symbol is for utf from Unknown user to item VX-123")