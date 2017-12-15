import os

if 'CI' not in os.environ and 'CIRCLECI' not in os.environ:
    from plugin import *