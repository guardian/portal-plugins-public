import unittest2
from django.core.management import execute_from_command_line
from django.conf import settings
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
        self.assertEqual(result,[0.0, 1.5975781630141477e-10, 5.650631737882143e-09, 0.0, 7.121341722924416e-09, 0.0, 0.0, 0.0, 0.0, 0.0, 2.1967614758862637e-10, 0.0])

    def test_absolute_get_total_other(self):
        from portal.plugins.gnmplutostats.views import ProjectInfoGraphView

        v = ProjectInfoGraphView()
        result = v.get_total_other("KP-2",self.explicitly_accounted_for,self.storage_capacities,relative=False)
        self.assertEqual(result,2009)

    def test_relative_get_total_other(self):
        from portal.plugins.gnmplutostats.views import ProjectInfoGraphView

        v = ProjectInfoGraphView()
        result = v.get_total_other("KP-2",self.explicitly_accounted_for,self.storage_capacities,relative=True)
        self.assertEqual(result,1.0968231073821473e-08)

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
        print result
        self.assertTrue(self.allUnique(result))