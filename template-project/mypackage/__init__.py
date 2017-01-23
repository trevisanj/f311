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
from .gear import *
from .datatypes import *
from .util import *
from .vis import *
from .gui import *

# # Function to access package-specific config file
#   ===============================================
def get_config():
    """Returns AAConfigObj object that corresponds to file ~/.mypackage.conf"""
    return a99.get_config_obj(".my_package.conf")


# # Function to be called from a99 package
#   ==========================================
# **Note** a99 collects File* and Vis* classes automatically
#          (from 'datafile' and 'vis' modules respectively).
#          To intervene manually, uncomment the following def
#
# def _setup_astroapi():
#     """
#     Adds entries to a99 class lists for different purposes
#     """
#
#     file_classes = a99.get_classes_in_module(datatypes, ex.DataFile)
#
#     # Classes to consider when attempts to load a text file (see a99.load_any_file())
#     a99._classes_txt.extend([class_ for class_ in file_classes if class_.flag_txt])
#     # Classes to consider when attempts to load a binary file (see a99.load_any_file())
#     a99._classes_bin.extend([class_ for class_ in file_classes if not class_.flag_txt])
#     # Adds Classes to consider when attempts to load a spectrum file (see a99.load_spectrum())
#     a99._classes_sp.extend([class_ for class_ in file_classes if issubclass(class_, a99.FileSpectrum)])
#     # All kwown File* classes
#     a99._classes_file.extend(file_classes)
#     # All kwnown Vis* classes
#     a99._classes_vis.extend(a99.get_classes_in_module(vis, a99.Vis))


# # Finally, gets rid of unwanted symbols in the workspace
#   ======================================================
del an