"""
Multiplicity (Chemistry)

https://en.wikipedia.org/wiki/Multiplicity_(chemistry)

  - Formulas to calculate the Hönl-London factors
  - Conversion from quantum information to branch label such as P/Q/R/P1/Q1 etc.

Note: This package will preserve the namespace hierarchy because there are repeated method names, e.g.,
`quanta_to_branch()`
"""


#
# _J2L_MAP = {"P": -1, "Q": 0, "R": 1}
# def branch_to_J2l(br):
#     """Converts P/Q/R to -1/0/+1
#
#     Tolerant to strings such as "P1", "P12" etc. (i.e., takes only the first character)"""
#     return _J2L_MAP[br[0]]


from collections import defaultdict
class honllondon_defaultdict(defaultdict):
    """
    Subclass of defaultdict to pass (the missing key, mol_consts) to the default factory

    Note: the missing key must be (vl, v2l, J), i.e., vibrational levels and rotational level
          (J = J2l)

    Usage:

        d = honllondon_keydefaultdict(C)
        d[x] # returns C(x, state_const)

    Source: solution by Rochen Ritzel at https://stackoverflow.com/questions/2912231/is-there-a-clever-way-to-pass-the-key-to-defaultdicts-default-factory
    """

    def __init__(self, mol_consts, *args, **kwargs):
        defaultdict.__init__(self, *args, **kwargs)
        self._mol_consts = mol_consts

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key, self._mol_consts)
            return ret
# del defaultdict


from . import singlet
from . import doublet
from . import triplet