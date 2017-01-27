"""
Object-oriented framework to handle file types:

  - Base class `FilePy` to support Python sources as config files
  - `FileLiteDB` class wraps a SQLite3 database
  - Automatic file type detection
  - Plugin system to support (read/write/visualize) new file types
"""


from . import gui
from . import vis
from . import blocks

from .basic import *
from .gui import *
from .vis import *
from .blocks import *
from .util import *
from .classcatalog import *
from .blocks import *
from .from_vald import *


# # Function to access package-specific config file
def get_config():
    """Returns AAConfigObj object that corresponds to file ~/.MY-PACKAGE-NAME.conf"""
    import a99
    return a99.get_config_obj(".f311.explorer.conf")
