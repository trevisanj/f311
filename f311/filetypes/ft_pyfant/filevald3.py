"""VALD3 atomic or molecular lines file"""


__all__ = ["FileVald3", "Vald3MolecularLine", "Vald3SolKey"]

# from ..gear import *
import sys
import a99
from .. import DataFile
import io
from collections import namedtuple, defaultdict

#: List of all atomic symbols
_symbols = [
'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si',
 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co',
 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr',
 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I',
 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy',
 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au',
 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U',
 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db',
 'Sg', 'Bh', 'Hs', 'Mt'
]


@a99.froze_it
class Vald3Species(a99.AttrsPart):
    """
    Represents species of VALD3 **extended format** atomic/molecular lines file

    Args:
        formula: e.g., "OH", "Fe"
        ioni: ionization level, >= 1


    Examples: "OH 1", "Fe 2"

    """
    attrs = ["formula", "ioni"]

    # # Properties that iterate through the Vald3Line objects to mount vectors
    # @property
    # def lambda_(self):
    #     return np.array([x.lambda_ for x in self.lines])

    def __init__(self):
        a99.AttrsPart.__init__(self)
        self.lines = []  # list of Vald3Line
        self.formula = None
        self.ioni = None

    def __len__(self):
        return len(self.lines)

    def __str__(self):
        return "{} {}".format(self.formula, self.ioni)

    def __repr__(self):
        return "'%s%s'" % (self.formula, self.ioni)

    def __iter__(self):
        return iter(self.lines)

    def _cut(self, llzero, llfin):
        """Keeps only the lines with their llzero <= lambda_ <= llfin."""
        for i in reversed(list(range(len(self)))):
            if not (llzero <= self.lines[i].lambda_ <= llfin):
                del self.lines[i]


# TODO Today I leave it like this, but tomorrow I must group the (system+vl,v2l)

# @a99.froze_it
# class Vald3Line(a99.AttrsPart):
#     attrs = ["lambda_", "loggf", "Jl", "J2l", "vl", "v2l"]
#
#     def __init__(self):
#         a99.AttrsPart.__init__(self)
#
#         self.lambda_ = None
#         self.loggf = None
#         self.Jl = None
#         self.J2l = None
#         self.vl = None
#         self.v2l = None
#         self.sys0 = None
#         self.sys1 = None
#         self.sys2 = None


Vald3MolecularLine = namedtuple("Vald3MolecularLine", ["lambda_", "loggf", "Jl", "J2l"])
Vald3SolKey = namedtuple("Vald3SolKey", ["vl", "v2l", "sys00", "sys01", "sys02", "sys10", "sys11", "sys12"])

class FileVald3(DataFile):
    """
    VALD3 atomic or molecular lines file

    Args:
        flag_parse_atoms=True: whether or not to parse the atomic lines
        flag_parse_molecules=True: whether or not to parse the molecular lines


    Species are encoded as follows.

    self.speciess (double s) is a dictionary where

        key: (formula, ionization), e.g. ("MgH", 1)
        value: "sets of lines", dict where

            key: 0 (int) if atom (not implemented)
                 (vl, v2l, sys00, sys01, sys02, sys10, sys11, sys12) if molecule
            value: list of Vald3AtomicLine if atom (not implemented yet)
                   list of Vald3MolecularLine if molecule

    TODO: parsing of atomic lines!

    **Note** Load only

    **Note** Does not load all file fields, only those needed to convert this file to
             PFANT molecular lines format (20161216)
    """

    attrs = ["speciess", "num_lines"]

    @property
    def num_lines(self):
        ret = sum(map(len, self.speciess))
        return ret

    def __len__(self):
        return len(self.speciess)

    def __init__(self, flag_parse_atoms=True, flag_parse_molecules=True):
        DataFile.__init__(self)

        # Configuration
        self.flag_parse_atoms = flag_parse_atoms
        self.flag_parse_molecules = flag_parse_molecules

        self.speciess = {}

    def __iter__(self):
        return iter(self.speciess)

    def _do_load(self, filename):
        """Clears internal lists and loads from file."""

        with open(filename, "r") as h:
            self._do_load_h(h, filename)

    def _do_load_h(self, h, filename):
        # ---SAMPLE FILE---
        #                                                                    Lande factors      Damping parameters
        # Elm Ion      WL_air(A)   log gf* E_low(eV) J lo  E_up(eV) J up  lower  upper   mean   Rad.  Stark  Waals
        # 'OH 1',       16401.409,  -8.587,  4.0602, 39.5,  4.8160, 39.5,99.000,99.000,99.000, 0.000, 0.000, 0.000,
        # '  Hb                                                     2s2.3s2.1p3          X,2,1,f,40,3'
        # '  Hb                                                 2s2.3s2.1p3              X,2,1,f,39,7'

        r = 0  # counts rows of file
        self.speciess = defaultdict(lambda: defaultdict(lambda: []))
        try:
            # Uses header as "magic characters"
            s = h.readline().strip("\n")
            if s != "                                                                   Lande factors      Damping parameters":
                raise RuntimeError("This doesn't appear to be a VALD3 extended-format atomic/molecular lines file")
            r += 1
            h.readline()
            r += 1

            while True:
                # Line 1/4
                # ========
                #
                s = h.readline().strip()
                if len(s) == 0 or not s.startswith("'"):
                    # EOF: blank line or references section
                    break

                fields = s.split(",")
                formula, s_ioni = fields[0][1:-1].split(" ")

                if formula in _symbols:
                    r += 1
                    # Atom, skips altogether (skips next three lines and loops)
                    for _ in range(3):
                        h.readline()
                        r += 1
                    continue

                line = Vald3MolecularLine(lambda_=float(fields[1]),
                                          loggf=float(fields[2]),
                                          Jl=float(fields[6]),  # J_up
                                          J2l = float(fields[4])  # J_lo
                                          )
                r += 1

                # Line 2/4 and 3/4
                # ================
                #
                # Parses "molecular system" TODO rename this term later
                # TODO dunno what comes first, vl or v2l, but if it follows the file header,
                # v2l (v lower) should come first, because "J lo" comes before "J up" in the file header
                s = h.readline().strip()
                r += 1
                sys00, sys01, sys02, v2l = _parse_system(s)
                s = h.readline().strip()
                r += 1
                sys10, sys11, sys12, vl = _parse_system(s)

                species_key = (formula, int(s_ioni))
                sol_key = Vald3SolKey(vl, v2l, sys00, sys01, sys02, sys10, sys11, sys12)
                self.speciess[species_key][sol_key].append(line)

                # Line 4/4 (citation line (skips))
                # ================================
                #
                h.readline()
                r += 1

        except Exception as e:
            raise type(e)(("Error around %d%s row of file '%s'" %
                           (r + 1, a99.ordinal_suffix(r + 1), filename)) + ": " + str(
                e)).with_traceback(sys.exc_info()[2])

def _parse_system(s):
    """Parses "system" information from VALD3 string

    Args:
        s: string (see examples below)

    Examples of lines:

    ```
    '  Hb                                                  3s2.4s2.1p4.5s1          X,2,0,,19,3'
    '  Hb                                                 3s2.4s2.1p3.5s2          A,2,1,e,20,9'
    '  Hb                         2sg2.2su2.3sg1.1pu3                            a,3,1,e,29,3,g'
    '  Hb                         2sg2.2su1.3sg1.1pu3/2sg2.2su2.3sg1.1pg1.1pu2   d,3,1,e,29,2,g'
    ```

    Returns:
        tuple: (sys0, sys1, sys2, v), wheter

            - sys0, sys1, sys2: information about system, TODO rename when I know better their meanings);
            - v: quantum number, either vl or v2l
    """

    kk = s[s.find(",")-1:-1].split(",")
    ret = {}
    sys0 = kk[0]
    sys1 = int(kk[1])
    sys2 = int(kk[2])
    try:
        v = int(kk[-1])
    except ValueError:
        # This covers the case when last item is "g" (see example in docstring)
        v = int(kk[-2])
    return sys0, sys1, sys2, v


def _fake_file():
    """Returns StringIO file to test FileVald3 class"""

    f = io.StringIO()
    f.write("""                                                                   Lande factors      Damping parameters
Elm Ion      WL_air(A)   log gf* E_low(eV) J lo  E_up(eV) J up  lower  upper   mean   Rad.  Stark  Waals
'Fe 1',       16400.045,  -4.131,  6.5922,  6.0,  7.3480,  5.0, 1.320, 1.090, 1.910, 8.140,-3.840,-7.330,
'  LS                                                                       3d7.(4F).4d f5G'
'  JK                                                             3d7.(4F<7/2>).4f 2[11/2]*'
'K14               Kurucz Fe I 2014   1 K14       1 K14       1 K14       1 K14       1 K14       1 K14       1 K14       1 K14       1 K14     Fe            '
'CO 1',       16400.058,  -5.951,  1.3820, 38.0,  2.1378, 39.0,99.000,99.000,99.000, 2.000, 0.000, 0.000,
'  Hb                                                4s2.5s2.1p4              X,2,0,,none,4'
'  Hb                                                    4s2.5s2.1p4          X,2,0,,none,7'
'KCO                                  2 KCO       2 KCO       2 KCO       2 KCO       2 KCO       2 KCO       2 KCO       2 KCO       2 KCO     (12)C(16)O    '
'CO 1',       16400.090,  -8.995,  1.1482, 53.0,  1.9040, 54.0,99.000,99.000,99.000, 2.000, 0.000, 0.000,
'  Hb                                                4s2.5s2.1p4              X,2,0,,none,2'
'  Hb                                                    4s2.5s2.1p4          X,2,0,,none,5'
'KCO                                  2 KCO       2 KCO       2 KCO       2 KCO       2 KCO       2 KCO       2 KCO       2 KCO       2 KCO     (12)C(18)O    '
""")

    f.seek(0)
    return f

def _test():
    """Test code in docstring

    Example:

    >>> h = _fake_file()
    >>> f = FileVald3()
    >>> f._do_load_h(h, "_fake_file")
    """
    return

# h = _fake_file()
# f = FileVald3()
# f._do_load_h(h, "_fake_file")



