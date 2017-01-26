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

from .gui import *
from .vis import *
from .blocks import *
from .paths import *
from .util import *
from .collaborate import *