import logging
logger = logging.getLogger(__name__)

#see http://thecodeship.com/patterns/guide-to-python-function-decorators/ for more information on how/why this works
def has_group(groupname):
    def hasgroup_inner(func):
        def func_wrapper(request):
            from pprint import pprint
            from django.core.exceptions import PermissionDenied
            #logger.debug("Current group list: {0}".format(",".join(request.user.groups.all())))

            #pprint(request.user.__dict__)
            for g in request.user.groups.all():
                pprint(g)
                logger.debug("user {0} is a member of {1}...".format(request.user.username,g.name))
                if g.name==groupname:
                    return func(request)

            logger.error("User {0} is not a member of the group {1}, so denying access".format(request.user.username,groupname))
            raise PermissionDenied
        return func_wrapper
    return hasgroup_inner