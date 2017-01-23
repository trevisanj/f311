"""
Multiplicity (Chemistry)

https://en.wikipedia.org/wiki/Multiplicity_(chemistry)

  - Formulas to calculate the Hönl-London factors
  - Conversion from quantum information to branch label such as P/Q/R/P1/Q1 etc.

Note: This package will preserve the namespace hierarchy because there are repeated method names, e.g.,
`quanta_to_branch()`
"""



_J2L_MAP = {"P": -1, "Q": 0, "R": 1}
def branch_to_J2l(br):
    """Converts P/Q/R to -1/0/+1

    Tolerant to strings such as "P1", "P12" etc. (i.e., takes only the first character)"""
    return _J2L_MAP[br[0]]


from . import singlet
from . import doublet
