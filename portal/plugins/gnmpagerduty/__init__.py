import os
if not "CI" in os.environ:
    from plugin import *

__version__ = 'DISPLAY_VERSION'
__production__ = False
