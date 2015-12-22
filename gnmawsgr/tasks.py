import celery

@celery.task
def glacier_restore(itemid,path):
    #print itemid
    #print '\n'
    #print path
    return 'Finished'



