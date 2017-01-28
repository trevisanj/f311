"""VALD3 atomic or molecular lines file"""


__all__ = ["Vald3Species", "FileVald3", "Vald3Line"]

# from ..gear import *
import sys
import a99
from .. import DataFile
import io


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

    def __init__(self, formula=None, ioni=None):
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


@a99.froze_it
class Vald3Line(a99.AttrsPart):
    attrs = ["lambda_", "loggf", "Jl", "J2l", "vl", "v2l"]

    def __init__(self):
        a99.AttrsPart.__init__(self)

        self.lambda_ = None
        self.loggf = None
        self.Jl = None
        self.J2l = None
        self.vl = None
        self.v2l = None


class FileVald3(DataFile):
    """
    VALD3 atomic or molecular lines file

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

    def __init__(self):
        DataFile.__init__(self)

        # list of Atom objects
        self.speciess = []

    def __iter__(self):
        return iter(self.speciess)

    def remove_formula(self, formula):
        """Removes given element (any ionization level)."""
        formula = ft.adjust_atomic_symbol(formula)
        for i in reversed(list(range(len(self)))):
            atom = self.speciess[i]
            if atom.formula == formula:
                del self.speciess[i]


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
        speciess = {}
        try:
            # Uses header as "magic characters"
            s = h.readline().strip("\n")
            if s != "                                                                   Lande factors      Damping parameters":
                raise RuntimeError("This doesn't appear to be a VALD3 extended-format atomic/molecular lines file")
            r += 1
            h.readline()
            r += 1

            while True:
                line = Vald3Line()

                s = h.readline().strip()
                if len(s) == 0 or not s.startswith("'"):
                    # EOF: blank line or references section
                    break

                fields = s.split(",")
                formula, s_ioni = fields[0][1:-1].split(" ")
                line.lambda_ = float(fields[1])
                line.loggf = float(fields[2])
                line.Jl = float(fields[6])  # J_up
                line.J2l = float(fields[4])  # J_lo
                r += 1


                if formula in a99.symbols:
                    # Skips energy levels information for the atoms
                    for _ in range(2):
                        h.readline()
                        r += 1
                else:
                    s = h.readline().strip()
                    line.vl = float(s[s.rfind(",") + 1:-1])  # v superior / v upper
                    r += 1
                    s = h.readline().strip()
                    line.v2l = float(s[s.rfind(",") + 1:-1])  # v inferior / v lower
                    r += 1

                key = formula + s_ioni  # will gb.py elements by this key
                if key in speciess:
                    a = speciess[key]
                else:
                    a = speciess[key] = Vald3Species()
                    a.formula = formula
                    a.ioni = int(s_ioni)
                    self.speciess.append(a)
                a.lines.append(line)

                # Skips the citation line
                h.readline()
                r += 1

        except Exception as e:
            raise type(e)(("Error around %d%s row of file '%s'" %
                           (r + 1, a99.ordinal_suffix(r + 1), filename)) + ": " + str(
                e)).with_traceback(sys.exc_info()[2])


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
