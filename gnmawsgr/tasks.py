import celery

@celery.task
def glacier_restore(filepath="", filename=""):
    test = filepath + filename
    print test
    return test



