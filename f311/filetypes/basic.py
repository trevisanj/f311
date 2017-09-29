"""
Miscellanea of basic routines used to implement the file classes
"""

import re
import os
import shutil
import sys
import a99


__all__ = ["adjust_atomic_symbol", "description_to_symbols", "symbols_to_formula",
           "iz_to_branch", "branch_to_iz",
           "get_default_data_path", "iz_to_branch_alt", "branch_to_iz_alt",
           "mol_consts_to_system_str", "greek_to_spdf", "spdf_to_greek",
           "SS_PLAIN", "SS_ALL_SPECIAL", "SS_RAW", "SS_SUPERSCRIPT"
           ]


# **        ****                ******        ****                ******        ****
#   **    **    ******    ******      **    **    ******    ******      **    **    ******    ******
#     ****            ****              ****            ****              ****            ****
#
# Conversion and formatting routines: Atomic symbols and formulas


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


def symbols_to_formula(symbols):
    """Converts two symbols to a formula as recorded in the 'molecule' table

    Args:
        symbols: 2-element list as returned by f311.filetypes.basic.description_to_symbols()

    Returns:
        str: examples: 'MgH', 'C2', 'CH'

    Formulas in the 'molecule' table have no isotope information
    """
    rec = re.compile("[a-zA-Z]+")
    symbols_ = [rec.search(x).group().capitalize() for x in symbols]
    symbols_ = ["C" if x == "A" else x for x in symbols_]
    if symbols_[0] == symbols_[1]:
        return "{}{}".format(symbols_[0], "2")
    else:
        return "".join(symbols_)

# **        ****                ******        ****                ******        ****
#   **    **    ******    ******      **    **    ******    ******      **    **    ******    ******
#     ****            ****              ****            ****              ****            ****
#
# Conversion and formatting routines: Branch-related
#

_iz_to_branch_map = {"1": "P", "2": "Q", "3": "R", "4": "P1", "5": "Q1", "6": "R1", "7": "P2",
                     "8": "Q2", "9": "R2", "10": "P3", "11": "Q3", "12": "R3", }
_branch_to_iz_map = dict(((value, key) for key, value in _iz_to_branch_map.items()))


# alternative mapping
_iz_to_branch_map_alt = {"1": "P1","2": "P12","3": "P21","4": "P2","5": "Q1","6": "Q12",
                         "7": "Q21","8": "Q2","9 ": "R1","10": "R12","11": "R21","12": "R2",}
_branch_to_iz_map_alt = dict(((value, key) for key, value in _iz_to_branch_map_alt.items()))


def iz_to_branch(iz):
    """Converts BLB's 'iz' code to string P/Q/R/P1. Inverse of branch_to_iz()

    (see pfantlib.90:read_molecules())

    **Note** iz-to-branch conversion cannot be trusted because different molecules use different
             conventions. To solve this in the future, new PFANT molecular lines .dat files will
             have branch saved as string.

    TODO note above is important
    """
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


# **        ****                ******        ****                ******        ****
#   **    **    ******    ******      **    **    ******    ******      **    **    ******    ******
#     ****            ****              ****            ****              ****            ****
#
# Multiplicity- and spdf-related conversion and formatting routines

# # System styles
# Example: "A 2 SIGMA - X 2 PI"
SS_PLAIN = -1
# multiplicity as superscript, spdf as Greek letter name
SS_SUPERSCRIPT = 2
# multiplicity as superscript, spdf as Greek letter
SS_ALL_SPECIAL = 0
# Does not convert SPDF to string. Example: "A 2 0 - X 2 1"
SS_RAW = 1

# superscript numbers
_INT_TO_SUPERSCRIPT = {1: "\u2071",
                       2: "\u00b2",
                       3: "\u00b3",
                       4: "\u2074"}


__A = ["Sigma", "Pi", "Delta", "Phi"]

_SPDF_TO_GREEK = dict(zip(range(len(__A)), __A))
_GREEK_TO_SPDF = dict(zip(__A, range(len(__A))))

def greek_to_spdf(greek):
    """Converts Greek letter name (e.g., "sigma", "Sigma" (case **sensitive**)) to int value in [0, 1, 2, 3]"""
    try:
        ret = _GREEK_TO_SPDF[greek]
    except KeyError:
        raise ValueError("Invalid SPDF: '{}' (possible values: {})".format(greek, _SPDF_TO_GREEK))
    return ret

def spdf_to_greek(number):
    """Converts int value in [0, 1, 2, 3] to the name of a Greek letter (all uppercase)"""
    return _SPDF_TO_GREEK[number]


def mol_consts_to_system_str(mol_consts, style=SS_ALL_SPECIAL):
    """Compiles electronic system information into string

    Args:
        mol_consts: dict-like containing keys 'from_label', 'from_mult', 'from_spdf', 'to_label',
                    'to_mult', 'to_spdf'

        style: rendering style: one of SS_*

    Returns:
        str
    """

    if style == SS_PLAIN:
        fmult = lambda x: x
        fspdf = lambda x:spdf_to_greek(x)
    elif style == SS_ALL_SPECIAL:
        fmult = lambda x: _INT_TO_SUPERSCRIPT[x]
        fspdf = lambda x: a99.greek_to_unicode(spdf_to_greek(x).capitalize())
    elif style == SS_RAW:
        fmult = lambda x: x
        fspdf = lambda x: x
    elif style == SS_SUPERSCRIPT:
        fmult = lambda x: _INT_TO_SUPERSCRIPT[x]
        fspdf = lambda x:spdf_to_greek(x)
    else:
        raise ValueError("Invalid style: {}".format(style))

    return "{} {} {} - {} {} {}".format(mol_consts["from_label"], fmult(mol_consts["from_mult"]),
                                    fspdf(mol_consts["from_spdf"]), mol_consts["to_label"],
                                    fmult(mol_consts["to_mult"]), fspdf(mol_consts["to_spdf"]))


