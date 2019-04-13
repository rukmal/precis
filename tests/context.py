import logging
import os
import sys

# Setting logging level to 'DEBUG' for the debugger
logging.getLogger().setLevel(logging.DEBUG)

try:
    import precis
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath('../'))
    os.chdir(os.path.abspath('../'))
    import precis
