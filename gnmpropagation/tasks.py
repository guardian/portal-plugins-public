import celery
import logging
log = logging.getLogger(__name__)
#log.info('Testing logging outside Celery task')

try:
    logger = celery.utils.log.get_task_logger(__name__)
except AttributeError:
    logger = logging.getLogger('main')

def do_propagate(collectionid,field,switch):

    #from pprint import pprint

    do_task = do_propagate.delay(collectionid,field,switch)

    #pprint(do_task.__dict__)

@celery.task
def propagate(collectionid,field,switch):
    from vidispine.vs_collection import VSCollection, VSItem
    import traceback
    #from pprint import pprint
    try:
        import raven
        from django.conf import settings
        raven_client = raven.Client(settings.RAVEN_CONFIG['dsn'])

    except StandardError as e:
        logger.error("Raven client either not installed (pip install raven) or set up (RAVEN_CONFIG in localsettings.py).  Unable to report errors to Sentry")
        raven_client = None

    #print collectionid
    #print field
    #print switch

    VIDISPINE_URL = "http://127.0.0.1"
    VIDISPINE_USERNAME = "admin"
    VIDISPINE_PORT = 8080
    VIDISPINE_PASSWORD = "admin"

    setswitch = None

    if (field == 'gnm_storage_rule_sensitive') and (switch == '1'):
        setswitch = 'storage_rule_sensitive'

    if (field == 'gnm_storage_rule_deletable') and (switch == '1'):
        setswitch = 'storage_rule_deletable'

    if (field == 'gnm_storage_rule_deep_archive') and (switch == '1'):
        setswitch = 'storage_rule_deep_archive'

    if (switch != '1') and (switch != '0'):
        setswitch = switch

    from django.conf import settings

    collection_obj = VSCollection(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
    #collection_obj = VSCollection(url=VIDISPINE_URL,port=VIDISPINE_PORT,user=VIDISPINE_USERNAME,passwd=VIDISPINE_PASSWORD)
    collection_obj.populate(collectionid, specificFields=['title','gnm_asset_category'])

    for subitem in collection_obj.content(shouldPopulate=False):
        subitem.populate(subitem.name, specificFields=['title','gnm_asset_category','gnm_type',field])
        #pprint(subitem.__dict__)
        type = '(unknown)'
        if isinstance(subitem,VSItem):
            type = "item"
        elif isinstance(subitem,VSCollection):
            type = "collection"

        #print "Got {0} {1}".format(type, subitem.name)
        #for f in ['title','gnm_type','gnm_asset_category',field]:
        #    print "\t{0}: {1}".format(f,subitem.get(f))
        #print setswitch

        if subitem.get(field) != setswitch:
            subitem.set_metadata({field: setswitch})

if __name__ == '__main__':
    import sys
    #Use this statement to test from command line
    for arg in sys.argv:
        print arg

    do_propagate(sys.argv[1],sys.argv[2],sys.argv[3])

