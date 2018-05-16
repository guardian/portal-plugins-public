# -*- coding: utf-8 -*-
import unittest2
from django.core.management import execute_from_command_line
from django.core.urlresolvers import reverse
from django.conf import settings
from mock import MagicMock, patch
from rest_framework.test import APIClient
import os


class TestProjectInfoGraphView(unittest2.TestCase):
    @classmethod
    def setUpClass(cls):
        if settings.DATABASES['default']['NAME']=="":
            raise ValueError("tests misconfigured, need a local database path")
        if os.path.exists(settings.DATABASES['default']['NAME']):
            os.unlink(settings.DATABASES['default']['NAME'])

        execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        execute_from_command_line(['manage.py', 'loaddata', 'sizedata1.yaml'])

    @classmethod
    def tearDownClass(cls):
        pass

    storage_capacities = {u'KP-8': {'capacity': 107912097693696, 'state': u'NONE', 'freeCapacity': 5361136893952, 'type': u'LOCAL', 'id': u'KP-8'}, u'KP-9': {'capacity': 17985330741248, 'state': u'NONE', 'freeCapacity': 1021535019008, 'type': u'LOCAL', 'id': u'KP-9'}, u'KP-6': {'capacity': 107912097693696, 'state': u'NONE', 'freeCapacity': 5356878680064, 'type': u'LOCAL', 'id': u'KP-6'}, u'KP-2': {'capacity': 193186329275153, 'state': u'NONE', 'freeCapacity': 5625000000000, 'type': u'LOCAL', 'id': u'KP-2'}, u'KP-4': {'capacity': 107912097693696, 'state': u'NONE', 'freeCapacity': 5356026621952, 'type': u'LOCAL', 'id': u'KP-4'}, u'KP-5': {'capacity': 107912097693696, 'state': u'NONE', 'freeCapacity': 5356814831616, 'type': u'LOCAL', 'id': u'KP-5'}, u'KP-21': {'capacity': 107912097693696, 'state': u'NONE', 'freeCapacity': 5356221874176, 'type': u'LOCAL', 'id': u'KP-21'}, u'KP-3': {'capacity': 190472893542468, 'state': u'NONE', 'freeCapacity': 4117000000000, 'type': u'LOCAL', 'id': u'KP-3'}, u'KP-16': {'capacity': 107912097693696, 'state': u'NONE', 'freeCapacity': 5356865159168, 'type': u'LOCAL', 'id': u'KP-16'}, u'KP-71': {'capacity': 107912097693696, 'state': u'NONE', 'freeCapacity': 5356878680064, 'type': u'LOCAL', 'id': u'KP-71'}, u'KP-11': {'capacity': 17985330741248, 'state': u'NONE', 'freeCapacity': 6035813494784, 'type': u'LOCAL', 'id': u'KP-11'}, u'KP-7': {'capacity': 107912097693696, 'state': u'NONE', 'freeCapacity': 5356865159168, 'type': u'LOCAL', 'id': u'KP-7'}}
    all_storages = [
                       "KP-11",
                       "KP-16",
                       "KP-2",
                       "KP-21",
                       "KP-3",
                       "KP-4",
                       "KP-5",
                       "KP-6",
                       "KP-7",
                       "KP-71",
                       "KP-8",
                       "KP-9"
                   ]
    explicitly_accounted_for = {
        "KP-11": 0,
        "KP-16": 1,
        "KP-2": 2093,
        "KP-21": 0,
        "KP-3": 2091,
        "KP-4": 3,
        "KP-5": 5,
        "KP-6": 3,
        "KP-7": 2,
        "KP-71": 43,
        "KP-8": 432,
        "KP-9":6
    }

    def test_absolute_entries_for_project(self):
        from portal.plugins.gnmplutostats.views import ProjectInfoGraphView

        v = ProjectInfoGraphView()
        result = v.entries_for_project("KP-21048", self.all_storages, self.storage_capacities, relative=False)
        self.assertEqual(result,[0, 16, 1035, 0, 1296, 0, 0, 0, 0, 0, 22, 0])

    def test_relative_entries_for_project(self):
        from portal.plugins.gnmplutostats.views import ProjectInfoGraphView

        v = ProjectInfoGraphView()
        result = v.entries_for_project("KP-21048", self.all_storages, self.storage_capacities, relative=True)
        self.assertEqual(result,[0.0, 0.00016751821760616466, 0.005925120219830547, 0.0, 0.007467287404138122, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0002303471960464045, 0.0])

    def test_absolute_get_total_other(self):
        from portal.plugins.gnmplutostats.views import ProjectInfoGraphView

        v = ProjectInfoGraphView()
        result = v.get_total_other("KP-2",self.explicitly_accounted_for,self.storage_capacities,relative=False)
        self.assertEqual(result,2009)

    def test_relative_get_total_other(self):
        from portal.plugins.gnmplutostats.views import ProjectInfoGraphView

        v = ProjectInfoGraphView()
        result = v.get_total_other("KP-2",self.explicitly_accounted_for,self.storage_capacities,relative=True)
        self.assertEqual(result,0.011501030455690406)

    def test_counted_project_entres(self):
        from portal.plugins.gnmplutostats.views import ProjectInfoGraphView
        from portal.plugins.gnmplutostats.models import ProjectSizeInfoModel
        limit = 10

        all_projects = ProjectSizeInfoModel.objects.order_by('-size_used_gb').values('project_id').distinct()[0:limit]

        v = ProjectInfoGraphView()
        project_entries = map(lambda project_entry: {"project_id": project_entry.items()[0][1], "sizes": v.entries_for_project(project_entry.items()[0][1],self.all_storages,self.storage_capacities,relative=False)}, all_projects)
        result = v.counted_project_entries(project_entries, self.all_storages)
        self.assertDictEqual(result, {'KP-8': 170, 'KP-9': 0, 'KP-6': 16, 'KP-2': 6200, 'KP-4': 0, 'KP-5': 0, 'KP-21': 0, 'KP-3': 6240, 'KP-16': 66, 'KP-71': 0, 'KP-11': 0, 'KP-7': 16})

    #thanks to https://stackoverflow.com/questions/5278122/checking-if-all-elements-in-a-list-are-unique
    @staticmethod
    def allUnique(x):
        seen = set()
        return not any(i in seen or seen.add(i) for i in x)

    def test_dedupe_project_set(self):
        from portal.plugins.gnmplutostats.views import ProjectInfoGraphView
        from portal.plugins.gnmplutostats.models import ProjectSizeInfoModel
        limit = 10

        v = ProjectInfoGraphView()
        all_projects = ProjectSizeInfoModel.objects.order_by('-size_used_gb').values('project_id')

        result = v.dedupe_project_set(all_projects,limit)

        self.assertEqual(len(result),limit)
        self.assertTrue(self.allUnique(result))


class TestProjectStatusHistoryView(unittest2.TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     if settings.DATABASES['default']['NAME']=="":
    #         raise ValueError("tests misconfigured, need a local database path")
    #     if os.path.exists(settings.DATABASES['default']['NAME']):
    #         os.unlink(settings.DATABASES['default']['NAME'])
    #
    #     execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
    #     execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    #     execute_from_command_line(['manage.py', 'loaddata', 'sizedata1.yaml'])
    #
    # @classmethod
    # def tearDownClass(cls):
    #     pass

    def test_normal(self):
        """
        ProjectStatusHistoryView should return a list of project statuses
        :return:
        """
        from portal.plugins.gnmplutostats.project_history import ProjectHistory, ProjectHistoryChange
        from django.contrib.auth.models import User
        import datetime
        import pytz

        p = ProjectHistory("VX-123",load_now=False)
        p.changes = [
            ProjectHistoryChange("gnm_project_status","66BC6490-8FAA-445E-9D09-EA38708C1FA6","2018-01-01T00:00:00Z","fred","value1"),
            ProjectHistoryChange("gnm_project_status","66BC6490-8FAA-445E-9D09-EA38708C1FA6","2018-01-01T01:00:00Z","fred","value2"),
            ProjectHistoryChange("gnm_project_status","66BC6490-8FAA-445E-9D09-EA38708C1FA6","2018-01-01T02:00:00Z","fred","value3"),
        ]
        u = User(username="admin",is_superuser=True,is_staff=True)

        with patch('portal.plugins.gnmplutostats.views.ProjectStatusHistory.ProjectHistory', return_value=p) as mock_projecthisory_constructor:
            cli = APIClient()
            cli.force_authenticate(u)
            response = cli.get(reverse('projectstatus_history',kwargs={'project_id':"VX-123"}))
            self.assertEqual(response.status_code,200)
            mock_projecthisory_constructor.assert_called_once_with("VX-123")
            print response.data
            self.assertDictEqual(response.data[0],{'fieldname': u'gnm_project_status', 'uuid': u'66bc6490-8faa-445e-9d09-ea38708c1fa6', 'timestamp': datetime.datetime(2018, 1, 1, 0, 0, tzinfo=pytz.utc), 'user': u'fred', 'newvalue': u'value1'})
            self.assertDictEqual(response.data[1],{'fieldname': u'gnm_project_status', 'uuid': u'66bc6490-8faa-445e-9d09-ea38708c1fa6', 'timestamp': datetime.datetime(2018, 1, 1, 1, 0, tzinfo=pytz.utc), 'user': u'fred', 'newvalue': u'value2'})
            self.assertDictEqual(response.data[2],{'fieldname': u'gnm_project_status', 'uuid': u'66bc6490-8faa-445e-9d09-ea38708c1fa6', 'timestamp': datetime.datetime(2018, 1, 1, 2, 0, tzinfo=pytz.utc), 'user': u'fred', 'newvalue': u'value3'})
            self.assertEqual(len(response.data),3)


    def test_unicode(self):
        """
        ProjectStatusHistoryView should not choke on non-ascii chars
        :return:
        """
        from portal.plugins.gnmplutostats.project_history import ProjectHistory, ProjectHistoryChange
        from django.contrib.auth.models import User
        import datetime
        import pytz
        p = ProjectHistory("VX-123",load_now=False)
        p.changes = [
            ProjectHistoryChange("gnm_project_status","66BC6490-8FAA-445E-9D09-EA38708C1FA6","2018-01-01T00:00:00Z","fred","välu€1"),
            ProjectHistoryChange("gnm_project_status","66BC6490-8FAA-445E-9D09-EA38708C1FA6","2018-01-01T01:00:00Z","fred","value2"),
            ProjectHistoryChange("gnm_project_status","66BC6490-8FAA-445E-9D09-EA38708C1FA6","2018-01-01T02:00:00Z","fred","value3"),
        ]
        u = User(username="admin",is_superuser=True,is_staff=True)

        with patch('portal.plugins.gnmplutostats.views.ProjectStatusHistory.ProjectHistory', return_value=p) as mock_projecthisory_constructor:
            cli = APIClient()
            cli.force_authenticate(u)
            response = cli.get(reverse('projectstatus_history',kwargs={'project_id':"VX-123"}))
            self.assertEqual(response.status_code,200)
            mock_projecthisory_constructor.assert_called_once_with("VX-123")
            self.assertDictEqual(response.data[0],{'fieldname': u'gnm_project_status', 'uuid': u'66bc6490-8faa-445e-9d09-ea38708c1fa6', 'timestamp': datetime.datetime(2018, 1, 1, 0, 0, tzinfo=pytz.utc), 'user': u'fred', 'newvalue': u"välu€1"})
            self.assertDictEqual(response.data[1],{'fieldname': u'gnm_project_status', 'uuid': u'66bc6490-8faa-445e-9d09-ea38708c1fa6', 'timestamp': datetime.datetime(2018, 1, 1, 1, 0, tzinfo=pytz.utc), 'user': u'fred', 'newvalue': u'value2'})
            self.assertDictEqual(response.data[2],{'fieldname': u'gnm_project_status', 'uuid': u'66bc6490-8faa-445e-9d09-ea38708c1fa6', 'timestamp': datetime.datetime(2018, 1, 1, 2, 0, tzinfo=pytz.utc), 'user': u'fred', 'newvalue': u'value3'})
            self.assertEqual(len(response.data),3)
            print response.content
            print response.data