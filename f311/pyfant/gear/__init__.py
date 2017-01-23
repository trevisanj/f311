"""
Self-contained sub-library

  - **must not** import modules from outside this directory (self-contained)
  - should contain the most basic and general-purpose routines of the project
    (have in mind that it could make another API)
  - no project-specific hard-coded data
"""

from .conversion import *
from .misc import *