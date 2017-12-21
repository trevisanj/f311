# # Temporary imports
#   =================
# These modules should be be del'eted at the end
import a99


# # Setup
#   =====
SOME_CONSTANT = 10.
# .
# .
# .


# # Imports
#   =======
from .basic import *
from .filetypes import *
from .util import *
from .vis import *
from .gui import *

# # Function to access package-specific config file
#   ===============================================
def get_config():
    """Returns AAConfigObj object that corresponds to file ~/.mypackage.conf"""
    return a99.get_config_obj(".mypackage.conf")


# # Finally, gets rid of unwanted symbols in the workspace
#   ======================================================
del a99