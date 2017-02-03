from vsmixin import VSMixin, VSWrappedSearch
import httplib2
from itertools import chain, imap
import logging

logger = logging.getLogger(__name__)


class BulkRestorer(VSMixin):
    """
    Encapsulates the ability to do restores, focussing on large projects
    """
    should_restore_archive_statuses = [
        'Archived'
    ]
    
    def initiate_bulk(self, user, project_id, selection=None, inTest=False):
        """
        This is called from a view to initiate the restore, we store the information and then call out to Celery
        to do the actual work
        :param user: user object from request
        :param project_id: project id to restore
        :param selection: specific selection of item IDs to restore
        :return: ID of a BulkRestore model object
        """
        from models import BulkRestore
        from tasks import bulk_restore_main
        
        try:
            bulk_request = BulkRestore.objects.get(parent_collection=project_id)
        except BulkRestore.DoesNotExist:
            bulk_request = BulkRestore()
            bulk_request.parent_collection = project_id
            bulk_request.username = user.name
            bulk_request.number_already_going = 0
            bulk_request.number_queued = 0
            bulk_request.current_status = "Queued"
            bulk_request.number_requested = 0
            bulk_request.save()
            
        if not inTest:
            bulk_restore_main.delay(requestid=bulk_request.pk)
        return bulk_request.pk
    
    def collapse_field(self, field):
        if not 'value' in field: return []
        return map(lambda value: value['value'], field['value']) #filter(lambda entry: 'value' in entry, field['value']))
    
    def collapse_group(self, group):
        return dict(map(lambda field: (field['name'],self.collapse_field(field),), group['field']))
    
    def collapse_timespan(self, timespan):
        """
        this function iterates through all groups, collapsing each into a dictionary of field name->value list mappings
        to this, it adds another item of all fields not within supplementary groups
        and returns a list of these dictionaries
        :param timespan: timespan to work on
        :return: list of dictionaries
        """
        return \
            map(lambda group: self.collapse_group(group), timespan['group']) + \
            [dict(map(lambda field: (field['name'], self.collapse_field(field), ), timespan['field']))]
            
    
    def remerge(self, iterator):
        """
        takes an iterator of dictionaries and merges them
        :param iterator:
        :return:
        """
        rtn = {}
        for item in iterator:
            try:
                for k,v in item.items():
                    if not k in rtn:
                        rtn[k] = v
                    else:
                        rtn[k].append(v)
            except AttributeError:
                print "WARNING: got AttributeError on {0}".format(item)
                
        return rtn
    
    def remap_metadata(self, record):
        return {
            'itemId': record['id'],
            'fields': self.remerge(
                self.flatmap(lambda timespan: self.collapse_timespan(timespan), filter(lambda timespan: True if timespan['end']=='+INF' else False,record['metadata']['timespan']))
            )
        }

    @staticmethod
    def flatmap(f, items):
        return chain.from_iterable(imap(f, items))
    
    def bulk_restore_main(self, requestid):
        """
        Wrapper function for _bulk_restore_main for exception handling
        :param requestid:
        :return:
        """
        from models import BulkRestore
        
        try:
           bulk_request = BulkRestore.objects.get(pk=requestid)
        except BulkRestore.DoesNotExist:
            logger.error("Unable to initiate bulk restore on id {0} as it does not exist".format(requestid))
            raise
        
        try:
            bulk_request.current_status="Processing"
            bulk_request.save()
            self._bulk_restore_main(bulk_request)
            
            bulk_request.current_status="Success"
            bulk_request.save()
        except Exception as e:
            bulk_request.current_status="Failed"
            bulk_request.last_error = str(e)
            bulk_request.save()
            raise
        
    def _bulk_restore_main(self, bulk_request):
        """
        This is called from a Celery task to actually do the restore
        :param requestid: ID of a BulkRestore record
        :return: None
        """
        from pprint import pprint
        from tasks import glacier_restore
        from models import BulkRestore, restore_request_for
        from gnmvidispine.vs_item import VSItem
        from django.conf import settings
        from datetime import datetime
        
        page_size = 20
        counter = 1
        search_futures = []
        

        search_request = VSWrappedSearch({'__collection': bulk_request.parent_collection}, pagesize=page_size)
        search_futures.append(search_request.execute(start_at=counter,fieldlist=[
                                             'gnm_external_archive_external_archive_device',
                                             'gnm_external_archive_external_archive_path',
                                             'gnm_external_archive_external_archive_status',
                                             'gnm_external_archive_external_archive_report',
                                             'gnm_external_archive_external_archive_request'
                                         ])
                              )
        
        while True:
            #have the next page request going in the background while we process the results from the first one
            search_futures.append(search_request.execute(start_at=counter * page_size,fieldlist=[
                                             'gnm_external_archive_external_archive_device',
                                             'gnm_external_archive_external_archive_path',
                                             'gnm_external_archive_external_archive_status',
                                             'gnm_external_archive_external_archive_report',
                                             'gnm_external_archive_external_archive_request'
                                         ])
                                  )
            
            #wait for the previous page to complete and get the results
            resultdoc = search_futures.pop(0).waitfor_json()
            pprint(resultdoc)
            
            remapped_items = map(lambda item: self.remap_metadata(item), resultdoc['item'])

            for item in remapped_items:
                bulk_request.number_requested += 1
                if item['fields']['gnm_external_archive_external_archive_status'][0] == 'Archived':
                    rq = restore_request_for(item['itemId'], bulk_request.username, bulk_request.parent_collection, "READY")
                    glacier_restore.delay(rq.pk,item['itemId'])
                    new_report_line = "Initiating restore from collection {0}".format(bulk_request.parent_collection)
                    new_request = "Requested Restore"
                    bulk_request.number_queued += 1
                else:
                    logger.warning("item {0} from collection {1} is not being restored because its status is {2}".format(
                        item['itemId'],
                        bulk_request.parent_collection,
                        item['fields']['gnm_external_archive_external_archive_status'][0]
                    ))
                    new_report_line = "Not restoring with collection {0} because archive status was {1}".format(
                        bulk_request.parent_collection,
                        item['fields']['gnm_external_archive_external_archive_status'][0]
                    )
                    new_request = item['fields']['gnm_external_archive_external_archive_request']
                vsi = VSItem(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
                vsi.name = item['itemId']
                report_content = "\n".join([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + new_report_line,
                    item['fields']['gnm_external_archive_external_archive_report'][0]
                ])
                vsi.set({
                    'gnm_external_archive_external_archive_report': report_content,
                    'gnm_external_archive_external_archive_request': new_request
                },group="Asset")
                bulk_request.save()
                
            counter +=1
            if counter*page_size > resultdoc['hits']:
                break
        