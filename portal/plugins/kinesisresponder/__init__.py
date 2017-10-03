__version__ = '1.0'
__production__ = False
import os
if not 'CI' in os.environ:
    from plugin import *
