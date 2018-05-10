"""
This is where you can write a lot of the code that responds to URLS - such as a page request from a browser
or a HTTP request from another application.

From here you can follow the Cantemo Portal Developers documentation for specific code, or for generic 
framework code refer to the Django developers documentation. 

"""
import logging

import json
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.renderers import JSONRenderer, XMLRenderer, YAMLRenderer
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from vsmixin import VSMixin, StorageCapacityMixin, HttpError
from django.db.models import Count,Avg,Sum

log = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = 'gnmplutostats/index.html'


class InvalidPlutoType(StandardError):
    pass


class BaseStatsView(VSMixin, APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer

    recognised_types = {}
    interesting_fields = []

    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BaseStatsView, self).dispatch(request, *args, **kwargs)

    def get(self, request, type=""):
        from traceback import format_exc
        try:
            return self.inner_get(request, type=type)
        except StandardError as e:
            return Response({'status': 'error', 'exception': str(e), 'trace': format_exc()},status=400)

    def inner_get(self, request, type=None):
        raise StandardError("inner_get not implemented!")

    def process_facets(self,data):
        if not 'facet' in data:
            raise KeyError("Passed data does not contain facets")

        rtn = {}
        for block in data['facet']:
            rtn[block['field']] = (map(lambda x: {'category': x['fieldValue'], 'value': x['value']}, block['count']))
        return rtn


class GetLibraryStats(BaseStatsView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer

    recognised_types = {
        'FCS': {
            'names': [
                'FCS Media/Holding',
                'FCS online media',
                'FCS external media'
            ],
            'overlaps': [

            ]
        },
        'Rushes': {
            'names': [
                'Back up Guardian rushes',
                'Rushes/ParentProjectsHeld',
                'Rushes+Masters/DeepArchive'
            ],
            'overlaps': [
                [
                    'Back up Guardian rushes',
                    'Rushes/ParentProjectsHeld',
                ],
                [
                    'Back up Guardian rushes',
                    'Rushes+Masters/DeepArchive',
                ]
            ]
        }
    }

    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    def __init__(self, *args, **kwargs):
        self._agent = None

    def get_library_hits(self,libid):
        from xml.etree.cElementTree import Element,SubElement,tostring,fromstring
        headers, content = self._make_vidispine_request(self._agent,
                                     "GET",
                                     "/API/library/{0};number=0".format(libid),
                                     body="",
                                     headers={'Accept': 'application/xml'})
        data=fromstring(content)

        try:
            return int(data.find('{http://xml.vidispine.com/schema/vidispine}hits').text)
        except AttributeError as e: #normally, this means that there was no hits element
            log.error('No <hits> element returned for library {0}'.format(libid))
            return 0
        except ValueError as e: #normally, this means that we couldn't convert the string to integer
            log.error('Could not convert value "{0}" to integer for library {1}'.format(
                data.find('{http://xml.vidispine.com/schema/vidispine}hits'),
            libid))
            return 0

    def find_min(self, overlap, data):
        """
        Find the overlapping field with the minimum number of hits, i.e. the one that is contained within the others
        :param overlap: overlap definition, a list over overlapping field names
        :param data: data dict, containing fieldname -> count pairs
        :return: fieldname of the minimum
        """
        n=9999999999
        min_field = None

        for fieldname in overlap:
            log.debug("checking {0} for min".format(fieldname))
            if data[fieldname]<n:
                min_field = fieldname
                n = data[fieldname]
        return min_field, n

    def process_overlaps(self, type, data, want_total=False):
        """
        Uses any overlap statements in the report definition to make piechart-compatible data
        :param data: data dictionary
        :return: normalised data dict
        """
        if not type in self.recognised_types:
            return data

        for overlap in self.recognised_types[type]['overlaps']:
            min_field, min_val = self.find_min(overlap, data)
            for fieldname in overlap:
                if fieldname != min_field:
                    data[fieldname] -= min_val

        if want_total:
            total = 0
            for k,v in data.items():
                total += v
            data['total'] = total
        return data

    def inner_get(self, request, type=""):
        from portal.plugins.gnmlibrarytool.models import LibraryNickname
        from vsmixin import HttpError
        import httplib2
        from django.http import HttpResponseBadRequest
        import json
        counts = {}
        self._agent = httplib2.Http()

        if type=='all':
             for lib in LibraryNickname.objects.all():
                try:
                    counts[lib.nickname] = self.get_library_hits(lib.library_id)
                except HttpError as e:
                    log.warning(e)

        elif type in self.recognised_types:
            for libname in self.recognised_types[type]['names']:
                lib = LibraryNickname.objects.get(nickname=libname)
                try:
                    counts[lib.nickname] = self.get_library_hits(lib.library_id)
                except HttpError as e:
                    log.warning(e)
        else:
            return HttpResponseBadRequest("Report type not recognised")

        d = self.process_overlaps(type,counts)

        rtn = {
            'status': 'ok',
            'data': {
                type:
                    []
            }
        }

        #rtn['data'][type] = map(lambda k, v: {'category': k,'value': v}, d.items())
        for k,v in d.items():
            rtn['data'][type].append({'category': k,'value': v})
        return Response(rtn)


class GetStatsView(BaseStatsView):
    recognised_types = {
        'commission': {
            'status_field': 'gnm_commission_status',
            'vs_class': 'collection'
        },
        'project': {
            'status_field': 'gnm_project_status',
            'vs_class': 'collection'
        },
        'master': {
            'status_field': 'gnm_master_generic_status',
            'vs_class': 'item'
        },
    }
    interesting_fields = []

    def inner_get(self, request, type=""):
        from xml.etree.cElementTree import Element,SubElement,tostring
        import httplib2
        import json

        if not type.lower() in self.recognised_types:
            raise InvalidPlutoType("{0} is not a recognised pluto type".format(type))

        xmlroot = Element('ItemSearchDocument', {'xmlns': 'http://xml.vidispine.com/schema/vidispine'})
        fieldEl = SubElement(xmlroot, 'field')
        nameEl = SubElement(fieldEl,'name')
        nameEl.text = 'gnm_type'
        valueEl = SubElement(fieldEl, 'value')
        valueEl.text=type
        facetEl = SubElement(xmlroot, 'facet', {'count': 'true'})
        ffieldEl = SubElement(facetEl, 'field')
        ffieldEl.text = self.recognised_types[type]['status_field']

        searchDoc = tostring(xmlroot,encoding="UTF-8")

        (headers, content) = self._make_vidispine_request(httplib2.Http(),"PUT","/API/search;number=0",searchDoc,
                                               {'Accept': 'application/json'})

        return Response({'status': 'ok', 'data': self.process_facets(data)})


class StorageDashMain(TemplateView):
    template_name = "gnmplutostats/storage_dash.html"


class ProjectScanReceiptView(ListAPIView):
    from serializers import ProjectScanReceiptSerializer
    from models import ProjectScanReceipt
    serializer_class = ProjectScanReceiptSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, )
    renderer_classes = (JSONRenderer, XMLRenderer, YAMLRenderer, )
    model = ProjectScanReceipt

    def get_queryset(self):
        if 'start' in self.request.GET:
            start = int(self.request.GET['start'])
        else:
            start = 0

        if 'limit' in self.request.GET:
            end = start + int(self.request.GET['limit'])
        else:
            end = start + 100

        return self.model.objects.all().order_by('last_scan')[start:end]


class ProjectStatInfoList(ListAPIView):
    from serializers import ProjectSizeInfoSerializer
    from models import ProjectSizeInfoModel

    serializer_class = ProjectSizeInfoSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, )
    renderer_classes = (JSONRenderer, XMLRenderer, YAMLRenderer, )
    model = ProjectSizeInfoModel

    def get_queryset(self):
        limit=20
        if 'limit' in self.request.GET:
            limit=int(self.request.GET['limit'])

        start=0
        if 'start' in self.request.GET:
            start=int(self.request.GET['start'])
        if 'storage_id' in self.kwargs:
            return self.model.objects.filter(storage_id=self.kwargs['storage_id']).order_by('-size_used_gb')[start:start+limit]
        elif 'project_id' in self.kwargs:
            return self.model.objects.filter(project_id=self.kwargs['project_id']).order_by('-size_used_gb')[start:start+limit]
        else:
            return self.model.objects.all().order_by('-size_used_gb', 'project_id','storage_id')[start:start+limit]


class ProjectInfoGraphView(APIView, StorageCapacityMixin):
    from serializers import ProjectSizeInfoSerializer
    from models import ProjectSizeInfoModel

    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, )
    renderer_classes = (JSONRenderer, )

    def entry_for_record(self,proj_id,storage_id):
        try:
            return self.ProjectSizeInfoModel.objects.get(project_id=proj_id, storage_id=storage_id).size_used_gb
        except self.ProjectSizeInfoModel.DoesNotExist:
            return 0

    def entries_for_project(self,proj_id, all_storages, storage_capacities, relative=False):
        absolute_values = map(lambda storage_id: self.entry_for_record(proj_id,storage_id),all_storages)
        if not relative:
            return absolute_values

        relative_values = []
        for n in range(0,len(all_storages)):
            #this relies on storage_capacities
            storage_name = all_storages[n]
            try:
                used_capacity = float(storage_capacities[storage_name]['capacity']/1024**3) - float(storage_capacities[storage_name]['freeCapacity']/1024**3)
                #we store capacity in Gb, Vidispine stores it in bytes
                relative_values.append(float(absolute_values[n]) / used_capacity)
            except TypeError:
                log.error("could not convert {0} or {1}".format(absolute_values[n], storage_capacities[storage_name]['capacity']))
                relative_values.append(0)
        return relative_values

    def get_total_other(self, storage_id, explicit_projects, storage_capacities, relative=False):
        """
        work out how much on the storage is "other" projects, i.e. ones that we have not counted already but do have in the database
        :param storage_id: storage id to check
        :param storage_capacities: list of total storage capacities
        :param explicit_projects: hash of total storage accounted for through explicit project entries, keyed by storage
        :param relative: if True, express as a fraction of the total storage capacity
        :return: number
        """
        database_result = self.ProjectSizeInfoModel.objects.filter(storage_id=storage_id).aggregate(Sum('size_used_gb'))

        absolute_value = database_result['size_used_gb__sum'] - explicit_projects[storage_id]
        if not relative:
            return absolute_value

        used_capacity = float(storage_capacities[storage_id]['capacity']/1024**3) - float(storage_capacities[storage_id]['freeCapacity']/1024**3)
        relative_value = float(absolute_value)/used_capacity
        return relative_value

    def counted_project_entries(self, project_entries, all_storages):
        """
        return a hash indicating the total amount of storage for indicated in the project_entries structure
        :param project_entries:
        :param all_storages:
        :return: hash of storage_name -> total counted
        """
        rtn = {}
        for n in range(0,len(all_storages)):
            rtn[all_storages[n]] = 0

        for entry in project_entries:
            for n in range(0,len(all_storages)):
                rtn[all_storages[n]] += entry['sizes'][n]

        return rtn

    def get_total_uncounted(self, storage_id, storage_capacities, relative=False):
        """
        return a number indicating the total amount of storage that is not counted at all in the database
        :param storage_id: check this storage
        :param all_counted:
        :param storage_capacities:
        :param relative:
        :return:
        """
        database_result = self.ProjectSizeInfoModel.objects.filter(storage_id=storage_id).aggregate(Sum('size_used_gb'))
        used_capacity = float(storage_capacities[storage_id]['capacity']/1024**3) - float(storage_capacities[storage_id]['freeCapacity']/1024**3)
        absolute_value = used_capacity - database_result['size_used_gb__sum']

        if not relative:
            return absolute_value
        else:
            return float(absolute_value)/float(used_capacity)

    def dedupe_project_set(self, project_id_set, limit):
        """
        dedupes project entries based on project_id
        :param project_id_set: set of results as returned from django ORM .values()
        :param limit: maximmum results to return
        :return:
        """

        rtn = []
        it = project_id_set.iterator()
        while len(rtn)<limit:
            try:
                row = next(it)
                if not row['project_id'] in rtn:
                    rtn.append(row['project_id'])
            except StopIteration:
                break
        return rtn

    def get(self, request):
        limit=15
        if 'limit' in self.request.GET:
            limit = int(self.request.GET['limit'])
        relative=True
        if 'absolute' in self.request.GET:
            relative=False

        try:
            all_storages = sorted(map(lambda x: x.items()[0][1], self.ProjectSizeInfoModel.objects.values('storage_id').distinct()))
            storage_capacities = dict(map(lambda storage_id: (storage_id, self.get_storage_capacity(storage_id)), all_storages))
            #so, distinct() doesn't want to work here, when we are sorting on size_used_gb, so have to dedupe ourselves
            all_projects = self.dedupe_project_set(self.ProjectSizeInfoModel.objects.order_by('-size_used_gb').values('project_id'),limit)

            project_entries = map(lambda project_id: {"project_id": project_id, "sizes": self.entries_for_project(project_id,all_storages,storage_capacities,relative=relative)}, all_projects)
            explicit_projects = self.counted_project_entries(project_entries,all_storages)

            project_entries.append({
                "project_id": "Other",
                "sizes": map(lambda storage_id: self.get_total_other(storage_id, explicit_projects, storage_capacities, relative=relative), all_storages)
            })

            project_entries.append({
                "project_id": "Uncounted",
                "sizes": map(lambda storage_id: self.get_total_uncounted(storage_id, storage_capacities, relative=relative), all_storages)
            })

            return Response({"status":"ok",
                             "storage_key": all_storages,
                             "projects": project_entries
                             })
        except HttpError as e:
            log.error(str(e))
            return Response({"status":"error","error":"Unable to communicate with Vidispine","detail": str(e), "server_response":e.content})


class TotalSpaceByStorage(APIView,StorageCapacityMixin):
    from models import ProjectSizeInfoModel

    permission_classes = (IsAuthenticated, )
    authentication_classes = (BasicAuthentication, SessionAuthentication, )
    renderer_classes = (JSONRenderer, XMLRenderer, YAMLRenderer, )
    model = ProjectSizeInfoModel

    def get(self, request):
        storages = self.ProjectSizeInfoModel.objects.values('storage_id').distinct()
        result = {}
        for s in storages:
            try:
                storage_data = self.get_storage_capacity(s['storage_id'])
                storage_total = storage_data['capacity']/1024**3
            except HttpError as e:
                log.warn(str(e))
                storage_total = 200000

            result[s['storage_id']] = {
                "counted": self.ProjectSizeInfoModel.objects.filter(storage_id=s['storage_id']).aggregate(Sum('size_used_gb'))['size_used_gb__sum'],
                "total": storage_total
            }
        return Response(result)


class StorageCapacityView(APIView, StorageCapacityMixin):
    permission_classes = (IsAdminUser, )
    renderer_classes = (JSONRenderer, XMLRenderer, YAMLRenderer, )
    authentication_classes = (SessionAuthentication, )

    def get(self, request, storage_id):
        try:
            return Response(self.get_storage_capacity(storage_id))
        except HttpError as e:
            log.error(str(e))
            return Response({"status":"error","error": "vidispine returned an error", "detail":e.content},status=500)


class ProjectStatusHistory(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, XMLRenderer, YAMLRenderer, )
    authentication_classes = (SessionAuthentication, )

    from serializers import ProjectHistoryChangeSerializer
    from project_history import ProjectHistory

    def get(self, requests, project_id):
        try:
            h = self.ProjectHistory(project_id)
            results = map(lambda change: self.ProjectHistoryChangeSerializer(change).data, h.changes_for_field("gnm_project_status"))
            return Response(results)
        except Exception as e:
            return Response({"status":"error","detail":str(e)})


class ProjectScanStats(APIView):
    """
    Returns the amount of projects currently needing scan
    """
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )

    def get(self, request):
        from models import ProjectScanReceipt
        from queries import IN_PRODUCTION_NEED_SCAN, NEW_NEED_SCAN, OTHER_NEED_SCAN
        try:
            rtn = {
                "total": ProjectScanReceipt.objects.count(),
                "in_production_need_scan": IN_PRODUCTION_NEED_SCAN.count(),
                "new_need_scan": NEW_NEED_SCAN.count(),
                "other_need_scan": OTHER_NEED_SCAN.count()
            }
            return Response(rtn)
        except Exception as e:
            return Response({"status": "error", "detail": str(e)}, status=500)


class ProjectScanHealth(APIView):
    """
    Returns any projects that should have been scanned but have no scan data
    """
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, )

    def get(self, request):
        from models import ProjectScanReceipt, ProjectSizeInfoModel
        from queries import IN_PRODUCTION_DID_SCAN, NEW_DID_SCAN, OTHER_DID_SCAN
        problem_projects = []

        try:
            for entry in IN_PRODUCTION_DID_SCAN:
                if ProjectSizeInfoModel.objects.filter(project_id=entry.project_id).count()==0:
                    problem_projects.append(entry.project_id)
            for entry in NEW_DID_SCAN:
                if ProjectSizeInfoModel.objects.filter(project_id=entry.project_id).count()==0:
                    problem_projects.append(entry.project_id)
            for entry in OTHER_DID_SCAN:
                if ProjectSizeInfoModel.objects.filter(project_id=entry.project_id).count()==0:
                    problem_projects.append(entry.project_id)
            return Response({"status":"ok","problem_projects":problem_projects})
        except Exception as e:
            return Response({"status": "error", "detail": str(e)}, status=500)