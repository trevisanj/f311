__all__ = ["FileMolecules", "Molecule", "SetOfLines", "molconsts_to_molecule"]



import sys
import numpy as np
import a99
from .. import DataFile, adjust_atomic_symbol, branch_to_iz, iz_to_branch, description_to_symbols
from .. import basic
import re

# TODO figure out state_from, state_to

@a99.froze_it
class SetOfLines(a99.AttrsPart):
    """
    Represents a "Set-Of-Lines" (vibrational transition with unique (vl, v2l))

    **Attention** Some properties return numpy arrays despite internally the data is stored as lists.
                  This was a bad idea but I won't change this anymore to avoid breaking client code

    Args:
        vl=None: upper vibrational state (v')
        v2l=None: lower vibrational state (v")
        qqv=None: Franck-Condon Factor
        ggv=None: TODO ?doc? (calculated from diatomic molecular constants)
        bbv=None: TODO ?doc? (calculated from diatomic molecular constants)
        ddv=None: TODO ?doc? (calculated from diatomic molecular constants)
        fact=None: TODO ?doc? (usually =1.)
        state_from=None: Transition letter; however I am not sure whether this is the lower or upper,
                     but I suspect this is the lower one.
        state_to=None: Transition letter; however I am not sure whether this is the lower or upper,
                     but I suspect this is the upper one.
    """

    attrs = ["vl", "v2l", "qqv", "ggv", "bbv", "ddv", "fact", "num_lines", "state_from", "state_to"]

    @property
    def llzero(self):
        """Minimum wavelength"""
        return min(self.lmbdam)

    @property
    def llfin(self):
        """Maximum wavelength"""
        return max(self.lmbdam)


    def __init__(self, vl=-1, v2l=-1, qqv=0, ggv=0, bbv=0, ddv=0, fact=0,
                 state_from="", state_to=""):
        a99.AttrsPart.__init__(self)

        self.vl = vl
        self.v2l = v2l
        self.qqv = qqv
        self.ggv = ggv
        self.bbv = bbv
        self.ddv = ddv
        self.fact = fact
        # # Transitional information (not stored in PFANT molecular lines file)
        # Example: 'A', 'X'
        self.state_from = state_from
        self.state_to = state_to

        # Vectors are keps as lists in order to .append_line() to work
        self.lmbdam = []
        self.sj = []
        self.jj = []
        self.branch = []

    @property
    def num_lines(self):
        return len(self)

    def __len__(self):
        return len(self.lmbdam)

    def __repr__(self):
        return "{}({}, {}, {}, {}, {}, {}, {})".format(self.__class__.__name__,
            self.vl, self.v2l, self.qqv, self.ggv, self.bbv, self.ddv, self.fact)

    def __iter__(self):
        """Creates MyDBRow objects to represent each molecular line"""
        fieldnames = ["lmbdam", "sj", "jj", "branch"]
        for t in zip(self.lmbdam, self.sj, self.jj, self.branch):
            obj = a99.MyDBRow()
            for fieldname, value in zip(fieldnames, t):
                obj[fieldname] = value
            yield obj

    def cut(self, lzero, lfin):
        """Reduces the number of lines to only the ones whose lmbdam is inside [lzero, lfin]"""
        l, s, j, b = [], [], [], []
        for _l, _s, _j, _b in zip(self.lmbdam, self.sj, self.jj, self.branch):
            if lzero <= _l <= lfin:
                l.append(_l)
                s.append(_s)
                j.append(_j)
                b.append(_b)
        self.lmbdam, self.sj, self.jj, self.branch = l, s, j, b

    def append_line(self, lmbdam, sj, jj, branch):
        self.lmbdam.append(lmbdam)
        self.sj.append(sj)
        self.jj.append(jj)
        self.branch.append(branch)

    def sort(self):
        """Sorts by wavelength **in-place**"""

        ii = np.argsort(self.lmbdam)
        self.lmbdam = [self.lmbdam[i] for i in ii]
        self.sj = [self.sj[i] for i in ii]
        self.jj = [self.jj[i] for i in ii]
        self.branch = [self.branch[i] for i in ii]


@a99.froze_it
class Molecule(a99.AttrsPart):
    attrs = ["description", "symbols", "fe", "do", "mm", "am", "bm", "ua", "ub",
             "te", "cro", "s", "nv", "num_lines"]

    @property
    def llzero(self):
        """Minimum wavelength"""
        return min([a.llzero for a in self.sol])

    @property
    def llfin(self):
        """Maximum wavelength"""
        return max([a.llfin for a in self.sol])

    @property
    def lmbdam(self):
        return np.hstack([np.array(x.lmbdam) for x in self.sol])

    @property
    def sj(self):
        return np.hstack([np.array(x.sj) for x in self.sol])

    @property
    def jj(self):
        return np.hstack([np.array(x.jj) for x in self.sol])

    @property
    def branch(self):
        return np.hstack([np.array(x.branch) for x in self.sol])

    @property
    def nv(self):
        return len(self.sol)

    @property
    def num_lines(self):
        ret = sum(map(len, self.sol))
        return ret

    @property
    def formula(self):
        return "".join([s[0]+s[1].lower() if len(s.strip()) == 2 else s.strip() for s in self.symbols])

    @property
    def qqv(self):
        return [x.qqv for x in self.sol]

    @property
    def ggv(self):
        return [x.qqv for x in self.sol]

    @property
    def bbv(self):
        return [x.qqv for x in self.sol]

    @property
    def ddv(self):
        return [x.qqv for x in self.sol]

    def __init__(self):
        a99.AttrsPart.__init__(self)

        # # "titulo" part
        # (20161206) titulo is now used semantically: it has 3 fields separated by a "#":
        # 'description # isotopes # transitions'.
        #
        # For more information, refer to pfantlib.f90:read_molecules(),
        # look for where variable km_titulo is read from file
        #
        # "titulo" is loaded from file, but not used when saving the file
        self.titulo = ""
        self.description = ""
        self.symbols = None
        self.fe = 0.
        self.do = 0.
        self.mm = 0.
        self.am = 0.
        self.bm = 0.
        self.ua = 0.
        self.ub = 0.
        self.te = 0.
        self.cro = 0.
        self.s = 0.

        self.sol = []  # list of SetOfLines objects


    def __len__(self):
        """Returns number of set-of-lines."""
        return len(self.sol)

    def __iter__(self):
        return iter(self.sol)

    def __getitem__(self, *args):
        return self.sol.__getitem__(*args)


    def cut(self, lzero, lfin):
        """Reduces the number of lines to only the ones whose lmbdam is inside [lzero, lfin]"""

        for i in reversed(list(range(len(self)))):
            self.sol[i].cut(lzero, lfin)
            if len(self.sol[i]) == 0:
                del self.sol[i]


@a99.froze_it
class FileMolecules(DataFile):
    """
    PFANT Molecular Lines

    Rather than as read_molecules() in readers.f90, this class stores
    information for each molecule inside a Molecule object.
    """

    default_filename = "molecules.dat"
    attrs = ["titm", "num_lines"]
    editors = ["mled.py"]

    @property
    def llzero(self):
        """Minimum wavelength"""
        return min([a.llzero for a in self.molecules])

    @property
    def llfin(self):
        """Maximum wavelength"""
        return max([a.llfin for a in self.molecules])

    @property
    def num_lines(self):
        """Total number of spectral line, counting all molecules."""
        return sum([x.num_lines for x in self.molecules])

    @property
    def num_sols(self):
        """Total number of spectral line, counting all molecules."""
        return sum([len(x) for x in self.molecules])

    @property
    def lmbdam(self):
        return np.hstack([m.lmbdam for m in self.molecules])

    @property
    def sj(self):
        return np.hstack([m.sj for m in self.molecules])

    @property
    def jj(self):
        return np.hstack([m.jj for m in self.molecules])

    @property
    def branch(self):
        return np.hstack([m.branch for m in self.molecules])

    @property
    def qqv(self):
        return np.hstack([x.qqv for x in self.molecules])

    @property
    def ggv(self):
        return np.hstack([x.ggv for x in self.molecules])

    @property
    def bbv(self):
        return np.hstack([x.bbv for x in self.molecules])

    @property
    def ddv(self):
        return np.hstack([x.ddv for x in self.molecules])

    @property
    def description(self):
        return [m.description for m in self.molecules]

    @property
    def fe(self):
        return [m.fe for m in self.molecules]

    @property
    def do(self):
        return [m.do for m in self.molecules]

    @property
    def mm(self):
        return [m.mm for m in self.molecules]

    @property
    def am(self):
        return [m.am for m in self.molecules]

    @property
    def bm(self):
        return [m.bm for m in self.molecules]

    @property
    def ua(self):
        return [m.ua for m in self.molecules]

    @property
    def ub(self):
        return [m.ub for m in self.molecules]

    @property
    def te(self):
        return [m.te for m in self.molecules]

    @property
    def cro(self):
        return [m.cro for m in self.molecules]

    @property
    def s(self):
        return [m.s for m in self.molecules]

    def __init__(self):
        DataFile.__init__(self)

        # Array of Molecule objects
        self.molecules = []

        # Literal in second row of file, sortta used as a file title/description
        self.titm = ""

    def __len__(self):
        return len(self.molecules)

    def __iter__(self):
        return iter(self.molecules)

    def __getitem__(self, *args):
        return self.molecules.__getitem__(*args)

    def cut(self, lzero, lfin):
        """Reduces the number of lines to only the ones whose lmbdam is inside [lzero, lfin]"""

        for i in reversed(list(range(len(self)))):
            m = self.molecules[i]
            m.cut(lzero, lfin)
            if len(m) == 0:
                del self.molecules[i]

    def _do_load(self, filename):
        """Clears internal lists and loads from file."""

        with open(filename, "r") as h:
            r = 0 # counts rows of file
            try:
                number = int(h.readline())  # not used (see below)
                r += 1
                self.titm = a99.readline_strip(h)
                r += 1

                nv = a99.int_vector(h)  # number of transitions=sets-of-lines for each molecule
                r += 1
                # Uses length of nv vector to know how many molecules to read (ignores "number")
                num_mol = len(nv)

                for im in range(num_mol):
                    nvi = nv[im]

                    m = Molecule()
                    self.molecules.append(m)

                    m.titulo = a99.readline_strip(h)
                    a99.get_python_logger().debug('Reading %d%s molecule \'%s\'' % (im+1, a99.ordinal_suffix(im+1), m.titulo))

                    parts = [s.strip() for s in m.titulo.split("#")]
                    m.description = parts[0]
                    if len(parts) > 1:
                        # Found 'structure' in m.titulo
                        m.symbols = [adjust_atomic_symbol(s) for s in
                                     [s.strip() for s in parts[1].split(" ") if len(s.strip()) > 0]]
                    else:
                        # Will try to guess molecule by m.titulo's contents
                        temp = description_to_symbols(parts[0])
                        m.symbols = temp or []
                    transitions = []
                    if len(parts) > 2:
                        numbers = [int(float(x)) for x in re.findall('([0-9.]+)', parts[2])]
                        transitions = list(zip(numbers[0::2], numbers[1::2]))

                    r += 1
                    m.fe, m.do, m.mm, m.am, m.bm, m.ua, m.ub, m.te, m.cro = a99.float_vector(h)
                    r += 1

                    h.readline()  # Skips line which is blank in file
                                  # In readers.f90 the variables are ise, a0, a1, a2 a3, a4, als
                                  # but the pfant does not use them.
                    r += 1

                    m.s = float(h.readline())
                    r += 1

                    # These vectors must have nvi elements
                    s_v, r_inc = a99.multirow_str_vector(h, nvi, r)
                    r += r_inc
                    qqv = list(map(float, s_v))
                    s_v, r_inc = a99.multirow_str_vector(h, nvi, r)
                    r += r_inc
                    ggv = list(map(float, s_v))
                    s_v, r_inc = a99.multirow_str_vector(h, nvi, r)
                    r += r_inc
                    bbv = list(map(float, s_v))
                    s_v, r_inc = a99.multirow_str_vector(h, nvi, r)
                    r += r_inc
                    ddv = list(map(float, s_v))
                    s_v, r_inc = a99.multirow_str_vector(h, nvi, r)
                    r += r_inc
                    fact = list(map(float, s_v))
                    for name in ["qqv", "ggv", "bbv", "ddv", "fact"]:
                        v = eval(name)
                        if len(v) != nvi:
                            raise RuntimeError(
                                'Attribute %s of molecule #%d must be a vector with %d elements (has %d)' %
                                (name, im+1, nvi, len(v)))

                    # creates sets of lines and appends to molecule
                    for isol, (q, g, b, d, f) in enumerate(zip(qqv, ggv, bbv, ddv, fact)):
                        o = SetOfLines()
                        o.qqv = q
                        o.ggv = g
                        o.bbv = b
                        o.ddv = d
                        o.fact = f
                        if isol < len(transitions):
                            o.vl, o.v2l = transitions[isol]
                        m.sol.append(o)

                    # Now reads lines
                    sol_iter = iter(m.sol)  # iterator to change the current set-of-lines with the "numlin" flag
                    o = next(sol_iter)  # current set-of-lines
                    # o.lmbdam, o.sj, o.jj, o.branch = [], [], [], []
                    while True:
                        # Someone added "*" signs as a 6th column of some lines
                        # which was causing my reading to crash.
                        # Therefore I read the line and discard beyond the 5th column before
                        # converting to float
                        temp = a99.str_vector(h)
                        lmbdam = float(temp[0])
                        sj = float(temp[1])
                        jj = float(temp[2])
                        # Alphanumeric now iz = int(temp[3])
                        iz = temp[3]
                        numlin = int(temp[4])

                        r += 1

                        o.lmbdam.append(lmbdam)
                        o.sj.append(sj)
                        o.jj.append(jj)
                        o.branch.append(iz)

                        if numlin > 0:
                            if numlin == 9:
                                break
                            o = next(sol_iter)

                    a99.get_python_logger().info("Loading '{}': {}".format(filename, a99.format_progress(im+1, num_mol)))

                    if im+1 == num_mol:
                        break

                    # im += 1
            except Exception as e:
                raise type(e)(("Error around %d%s row of file '%s'" %
                    (r+1, a99.ordinal_suffix(r+1), filename))+": "+str(e)).with_traceback(sys.exc_info()[2])

    def _do_save_as(self, filename):
        with open(filename, "w") as h:
            a99.write_lf(h, str(len(self.molecules)))
            a99.write_lf(h, self.titm)
            a99.write_lf(h, " ".join([str(x.nv) for x in self.molecules]))
            for i_m, m in enumerate(self.molecules):
                a99.get_python_logger().info("Saving '{}': molecule {}/{}".format(filename, i_m+1, len(self.molecules)))

                # # Assembles "titulo"
                # ## Transitions
                ltrans = []
                for sol in m:
                    if sol.vl is None or sol.v2l is None:
                        break
                    ltrans.append([sol.vl, sol.v2l])
                new_titulo = "{} # {} # {}".\
                    format(m.description,
                           " ".join([s.strip() for s in m.symbols]),
                           "|".join(["{:.0f},{:.0f}".format(*t) for t in ltrans]))

                # - mled change, incorporate shit

                a99.write_lf(h, new_titulo)
                a99.write_lf(h, (" ".join(["%.10g"]*9)) % (m.fe, m.do, m.mm, m.am,
                    m.bm, m.ua, m.ub, m.te, m.cro))
                a99.write_lf(h, "")
                a99.write_lf(h, str(m.s))
                a99.write_lf(h, " ".join(["{:g}".format(x.qqv) for x in m.sol]))
                a99.write_lf(h, " ".join(["{:.2f}".format(x.ggv) for x in m.sol]))
                a99.write_lf(h, " ".join(["{:.5f}".format(x.bbv) for x in m.sol]))
                a99.write_lf(h, " ".join(["{:.2f}".format(x.ddv) for x in m.sol]))
                a99.write_lf(h, " ".join(["{:g}".format(x.fact) for x in m.sol]))

                num_sol = len(m.sol)
                for i, s in enumerate(m.sol):
                    num_lines = len(s)  # number of lines for current set-of-lines
                    for j in range(num_lines):
                        numlin = 0 if j < num_lines-1 else 9 if i == num_sol-1 else 1
                        a99.write_lf(h, "%.10g %.10g %.10g %s %d" %
                                     (s.lmbdam[j], s.sj[j], s.jj[j], s.branch[j], numlin))


def molconsts_to_molecule(molconsts):
    """Assembles a Molecule object from record from a FileMolDB database

    Args:
        molconsts: a dict-like object combining field values from tables 'molecule', 'state',
                    'pfantmol', and 'system' from a FileMolDB database
    """
    molconsts["system_str"] = molconsts.get_system_str(basic.SS_PLAIN)

    mol = Molecule()
    mol.description = "{formula} [{system_str}]".format(**molconsts)
    mol.symbols = description_to_symbols(molconsts["formula"])
    mol.fe = molconsts["fe"]
    mol.do = molconsts["do"]
    mol.mm = molconsts["am"] + molconsts["bm"]
    mol.am = molconsts["am"]
    mol.bm = molconsts["bm"]
    mol.ua = molconsts["ua"]
    mol.ub = molconsts["ub"]
    mol.te = molconsts["te"]
    mol.cro = molconsts.get_deltak()
    mol.s = molconsts.get_S2l()
    return mol