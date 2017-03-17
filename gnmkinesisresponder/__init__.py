__version__ = 'DISPLAY_VERSION'
__production__ = False
import os
if not 'CI' in os.environ:
    from plugin import *
