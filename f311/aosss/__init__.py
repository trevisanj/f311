'''"Adaptive Optics Systems Simulation Support"'''

# # Imports
from .basic import *
from .util import *
from .report import *
from .mosaic import *
from .util import *

# from . import basic
# from . import util
# from . import report
# from . import mosaic


# # Function to access package-specific config file
def get_config():
    """Returns AAConfigObj object that corresponds to file ~/.f311.aosss.conf"""
    import a99
    return a99.get_config_obj(".f311.aosss.conf")


