import os
from tasks import check_storage
if not "CI" in os.environ:
    from plugin import *

__version__ = 'DISPLAY_VERSION'
__production__ = False

if not "CI" in os.environ:
    check_storage.delay()

