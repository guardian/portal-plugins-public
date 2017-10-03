__author__ = 'localhome'
__version__ = "v0.1 development"
import os
if not 'CI' in os.environ:
    import plugin
