from plugin import *
from tasks import check_storage

__version__ = 'DISPLAY_VERSION'
__production__ = False

check_storage.delay()

