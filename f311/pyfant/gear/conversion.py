import re


__all__ = ["adjust_atomic_symbol", "description_to_symbols", "iz_to_branch", "branch_to_iz"]


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


_iz_to_branch_map = {"1": "P", "2": "Q", "3": "R", "4": "P1", "5": "Q1", "6": "R1", "7": "P2", "8": "Q2", "9": "R2", "10": "P3", "11": "Q3", "12": "R3",}
_branch_to_iz_map = dict(((value, key) for key, value in _iz_to_branch_map.items()))
def iz_to_branch(iz):
    """Converts BLB's 'iz' code to string P/Q/R/P1 ... (see pfantlib.90:read_molecules()"""
    return _iz_to_branch_map[str(iz)]

def branch_to_iz(br):
    """Converts branch P/Q/R/P1, etc. into BLB's 'iz' code"""
    return _branch_to_iz_map[br]
