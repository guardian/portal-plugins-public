import celery
import logging
log = logging.getLogger(__name__)

try:
    logger = celery.utils.log.get_task_logger(__name__)
except AttributeError:
    logger = logging.getLogger('main')
    #do_task = propagate.delay(collectionid,field,switch)

rule_value_table = {
    'gnm_storage_rule_sensitive': 'storage_rule_sensitive',
    'gnm_storage_rule_deletable': 'storage_rule_deletable',
    'gnm_storage_rule_deep_archive': 'storage_rule_deep_archive'
}


class UnknownFieldError(StandardError):
    pass

@celery.task
def propagate(collectionid,field,current_value):
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

    #setswitch = None

    # if (field == 'gnm_storage_rule_sensitive') and (switch == '1'):
    #     setswitch = 'storage_rule_sensitive'
    #
    # if (field == 'gnm_storage_rule_deletable') and (switch == '1'):
    #     setswitch = 'storage_rule_deletable'
    #
    # if (field == 'gnm_storage_rule_deep_archive') and (switch == '1'):
    #     setswitch = 'storage_rule_deep_archive'

    # try:
    #     if current_value is None or not current_value or current_value == "":
    #         setswitch = rule_value_table[field]
    #     else:
    #         setswitch = ""
    # except KeyError:
    #     logger.error("I can't propagate the value of {0} as I do not have the string value to set it to.  Check rule_value_table in gnmproparation:tasks.py")
    #     raise UnknownFieldError(field)
    #
    # if (switch != '1') and (switch != '0'):
    #     setswitch = switch

    from django.conf import settings

    collection_obj = VSCollection(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
    #collection_obj = VSCollection(url=VIDISPINE_URL,port=VIDISPINE_PORT,user=VIDISPINE_USERNAME,passwd=VIDISPINE_PASSWORD)
    collection_obj.populate(collectionid, specificFields=['title','gnm_asset_category'])

    n=0
    for subitem in collection_obj.content(shouldPopulate=False):
        logger.debug("propagating value from parent {0} to child {1} ({2})".format(collectionid,subitem.name,subitem.__class__))

        subitem.populate(subitem.name, specificFields=['title','gnm_asset_category','gnm_type','__collection_size',field])
        logger.debug(u"title: {0}, category: {1}, type: {2}".format(subitem.get('title'),subitem.get('gnm_asset_category'),
                                                                    subitem.get('gnm_type')))

        #pprint(subitem.__dict__)
        type = '(unknown)'
        if isinstance(subitem,VSItem):
            type = "item"
            try:
                if int(subitem.get('__collection_size')) > 1:
                    logger.warning("Item {0} in collection {1} is linked {2} times, so not flagging".format(
                        subitem.name,
                        collectionid,
                        subitem.get('__collection_size')
                    ))
                    continue
            except TypeError:
                #this means that __collection_size was None or an invalid value
                logger.warning("{0} {1} had no __collection_size".format(type,subitem.name))
            except StandardError as e:
                logger.error(e)
                if raven_client is not None: raven_client.captureException()
                raise
        elif isinstance(subitem,VSCollection):
            type = "collection"

        #print "Got {0} {1}".format(type, subitem.name)
        #for f in ['title','gnm_type','gnm_asset_category',field]:
        #    print "\t{0}: {1}".format(f,subitem.get(f))
        #print setswitch

        if subitem.get(field) != current_value:
            try:
                subitem.set_metadata({field: current_value})
            except StandardError as e:
                if raven_client is not None: raven_client.captureException()
                raise

        logger.info("value set on {0} {1}".format(type, subitem.name))
        n+=1

    logger.info("Propagation run completed for {0}.  Affected {1} items".format(collectionid, n))

if __name__ == '__main__':
    import sys
    #Use this statement to test from command line
    for arg in sys.argv:
        print arg

    propagate(sys.argv[1],sys.argv[2],sys.argv[3])
    #do_propagate(sys.argv[1],sys.argv[2],sys.argv[3])

