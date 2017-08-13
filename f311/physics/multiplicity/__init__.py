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


from ..molconsts import MolConsts

class honllondon_dict(dict):
    """
    Subclass of dict to deal with keys as (vl, v2l, J, branch)

    References:
        Based on solution by Rochen Ritzel at
        https://stackoverflow.com/questions/2912231/is-there-a-clever-way-to-pass-the-key-to-defaultdicts-default-factory
    """

    def __init__(self, mol_consts):
        if not isinstance(mol_consts, MolConsts):
            raise TypeError("mol_consts must be a MolConsts")
        dict.__init__(self)
        self._mol_consts = mol_consts

    def __missing__(self, key):
        self._populate_with_key(key)
        return self[key]

    def _populate_with_key(self, key):
        """Must be inherited and populate self with all branches for given (vl, v2l, J)"""
        raise NotImplementedError()


from . import singlet
from . import doublet
from . import triplet
