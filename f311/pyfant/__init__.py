# # Temporary imports
#   =================
# These modules should be be del'eted at the end
import a99


# # Setup
#   =====
SESSION_PREFIX_SINGULAR = 'session-'
SESSION_PREFIX_PLURAL = 'session-'
MULTISESSION_PREFIX = 'multi-session-'


# # Imports
#   =======
from .errors import *
from .gear import *
from .datatypes import *
from .conf import *
from .runnables import *
from .rm import *
from .vis import *
from .util import *
from .from_vald import *
from .multirunnable import *
from .gui import *
from .paths import *
from . import datatypes
from . import gear
from . import gui
from . import vis
from . import convmol


# # Function to access package-specific config file
#   ===============================================
def get_config():
    """Returns PyfantConfigObj object that corresponds to file ~/.ftpyfant.conf"""
    return a99.get_config_obj(".ftpyfant.conf")


# # Finally, gets rid of unwanted symbols in the workspace
#   ======================================================
del a99
