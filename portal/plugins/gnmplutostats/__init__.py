__version__ = '1.0.0'
__author__ = 'Andy Gallagher <andy.gallagher@theguardian.com>'
__production__ = False
import os

if not 'CI' in os.environ:
    from plugin import *
