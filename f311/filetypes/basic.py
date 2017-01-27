"""
Miscellanea of basic routines used to implement the file classes
"""

import re
import os
import shutil
import sys
from .. import filetypes as ft


__all__ = ["adjust_atomic_symbol", "description_to_symbols", "iz_to_branch", "branch_to_iz",
           "get_default_data_path"]


def adjust_atomic_symbol(x):
    """Makes sure atomic symbol is right-aligned and upper case (PFANT convention)."""
    assert isinstance(x, str)
    return "%2s" % (x.strip().upper())

# Formulas that can be recognized in PFANT molecule header information ("titulo")
# This exists for backward compatibility. New molecules should have its symbols informed separately
#
# **Careful** If you add entried, make sure everything is in uppercase
_BUILTIN_FORMULAS = {
     "MGH": ["MG", "H"],
     "C2": ["C", "C"],
     "CN": ["C", "N"],
     "CH": ["C", "H"],
     "13CH": ["A", "H"],
     "12C16O": ["C", "O"],
     "NH": ["N", "H"],
     "OH": ["O", "H"],
     "FEH": ["FE", "H"],
     "TIO": ["TI", "O"],
     "CO": ["C", "O"],
}


def description_to_symbols(descr):
    """Finds molecular formula in description text and returns separate symbols

    This routine is similar to pfantlib.f90:assign_symbols_by_formula()

    It is used when the symbols are not informed separately
    after the first "#" in the molecule 'titulo'

    Args:
        descr: e.g., "12C16O INFRARED  X 1 SIGMA+,   version 15/oct/98"

    Returns: list of two elements, e.g., ["MG", " H"]
    """

    descr = descr.upper()
    for formula, symbols in _BUILTIN_FORMULAS.items():
        # Searches for formula at start or after whitespace
        if re.search(r'(^|\W){}([^0-9A-Z]|$)'.format(formula), descr):
            return [adjust_atomic_symbol(x) for x in symbols]
    return None
    # raise RuntimeError("Could not find a valid formula in description '{}'".format(descr))


_iz_to_branch_map = {"1": "P", "2": "Q", "3": "R", "4": "P1", "5": "Q1", "6": "R1", "7": "P2",
                     "8": "Q2", "9": "R2", "10": "P3", "11": "Q3", "12": "R3", }
_branch_to_iz_map = dict(((value, key) for key, value in _iz_to_branch_map.items()))


def iz_to_branch(iz):
    """Converts BLB's 'iz' code to string P/Q/R/P1 ... (see pfantlib.90:read_molecules()"""
    return _iz_to_branch_map[str(iz)]


def branch_to_iz(br):
    """Converts branch P/Q/R/P1, etc. into BLB's 'iz' code"""
    return _branch_to_iz_map[br]


def get_default_data_path(*args, module=ft, class_=None):
    """
    Returns path to default data directory

    Arguments 'module' and 'class' give the chance to return path relative to package other than
    f311.filetypes

    Args:
        module: Python module object. It is expected that this module has a sub-subdirectory
                named 'data/default'
        class_: Python class object to extract path information from. If this argument is used,
                it will be expected that the class "root" package will have a subpackage called
                'filetypes', i.e., '(some package).filetypes'.
                **Has precedence over 'module' argument**

    """

    if class_ is not None:
        pkgname =  class_.__module__
        mseq = pkgname.split(".")
        if len(mseq) < 2 or mseq[1] != "filetypes":
            raise ValueError("Invalid module name for class '{}': '{}' "
                             "(must be '(...).filetypes[.(...)]')".format(class_.__name__, pkgname))
        module = sys.modules[".".join(mseq[:2])]
    module_path = os.path.split(module.__file__)[0]
    p = os.path.abspath(os.path.join(module_path, "data", "default", *args))
    return p


def copy_default_data_file(filename, module=ft):
    """Copies file from ftpyfant/data/default directory to local directory."""
    fullpath = get_default_data_path(filename, module=module)
    shutil.copy(fullpath, ".")
