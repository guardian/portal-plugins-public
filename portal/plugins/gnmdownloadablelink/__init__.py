import os

if not 'CI' in os.environ:
    from plugin import *
