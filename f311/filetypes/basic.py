"""
Miscellanea of basic routines used to implement the file classes
"""

import re
import os
import shutil
import sys


__all__ = ["adjust_atomic_symbol", "description_to_symbols", "iz_to_branch", "branch_to_iz",
           "get_default_data_path", "iz_to_branch_alt", "branch_to_iz_alt"]


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
        descr: string

    Returns:
        list of two elements, e.g., [" C", " O"]

    Example:

    >>> import f311.filetypes as ft
    >>> ft.description_to_symbols("12C16O INFRARED  X 1 SIGMA+,   version 15/oct/98")
    [' C', ' O']
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


# alternative mapping
_iz_to_branch_map_alt = {"1": "P1","2": "P12","3": "P21","4": "P2","5": "Q1","6": "Q12",
                         "7": "Q21","8": "Q2","9 ": "R1","10": "R12","11": "R21","12": "R2",}
_branch_to_iz_map_alt = dict(((value, key) for key, value in _iz_to_branch_map_alt.items()))



def iz_to_branch(iz):
    """Converts BLB's 'iz' code to string P/Q/R/P1. Inverse of branch_to_iz()

    (see pfantlib.90:read_molecules())"""
    return _iz_to_branch_map[str(iz)]


def branch_to_iz(br):
    """Converts branch P/Q/R/P1, etc. into BLB's 'iz' code

    Args:
        branch: str, [P/Q/R][/1/2/3], for example "P", "P1"

    Returns:
        str: from "1" to "12"
    """
    return _branch_to_iz_map[br]


def iz_to_branch_alt(iz):
    """Alternative mapping used by Bruno Castilho's CH. Inverse of branch_to_iz_alt()

    This is the mapping found in Bruno Castilho's work for molecule CH
    (directory ATMOS/wrk4/bruno/Mole/CH, check file, e.g., sja000.dat and source selech.f)
    """
    return _iz_to_branch_map_alt[str(iz)]


def branch_to_iz_alt(br):
    """
    Alternative mapping used by Bruno Castilho's CH

    Args:
        branch: str, [P/Q/R][1/12/21/2], for example "P1", "Q21"

    Returns:
        str: from "1" to "12"

    This is the mapping found in Bruno Castilho's work for molecule CH
    (directory ATMOS/wrk4/bruno/Mole/CH, check file, e.g., sja000.dat and source selech.f)
    """
    return _branch_to_iz_map_alt[br]

def get_default_data_path(*args, module=None, class_=None):
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
    if module is None:
        module = __get_filetypes_module()

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


def copy_default_data_file(filename, module=None):
    """Copies file from ftpyfant/data/default directory to local directory."""
    if module is None:
        module = __get_filetypes_module()
    fullpath = get_default_data_path(filename, module=module)
    shutil.copy(fullpath, ".")


def __get_filetypes_module():
    from f311 import filetypes as ft
    return ft

