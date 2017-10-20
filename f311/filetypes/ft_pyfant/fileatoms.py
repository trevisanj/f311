__all__ = ["FileAtoms", "Atom", "AtomicLine"]

# from ..gear import *
# from ..errors import *
import struct
import logging
import sys
import numpy as np
import tabulate
import a99
from .. import DataFile, adjust_atomic_symbol
import re

@a99.froze_it
class Atom(a99.AttrsPart):
    """
    Element with its atomic lines

    Atom is identified by key symbol+ionization
    """
    attrs = ["elem", "ioni"]

    @property
    def llzero(self):
        """Minimum wavelength"""
        return min([x.lambda_ for x in self.lines])

    @property
    def llfin(self):
        """Maximum wavelength"""
        return max([x.lambda_ for x in self.lines])

    # Properties that iterate through the AtomicLine objects to mount vectors
    @property
    def lambda_(self):
        return np.array([x.lambda_ for x in self.lines])
    @property
    def kiex(self):
        return np.array([x.kiex for x in self.lines])
    @property
    def algf(self):
        return np.array([x.algf for x in self.lines])
    @property
    def ch(self):
        return np.array([x.ch for x in self.lines])
    @property
    def gr(self):
        return np.array([x.gr for x in self.lines])
    @property
    def ge(self):
        return np.array([x.ge for x in self.lines])
    @property
    def zinf(self):
        return np.array([x.zinf for x in self.lines])
    @property
    def abondr(self):
        return np.array([x.abondr for x in self.lines])

    def __init__(self):
        a99.AttrsPart.__init__(self)
        self.lines = []  # list of AtomicLine
        self.elem = None
        self.ioni = None

    def __len__(self):
        return len(self.lines)

    def __str__(self):
        return "'{} {}' ({} lines)".format(self.elem, self.ioni, len(self))

    def one_liner_str(self):
        return self.__str__()

    def __repr__(self):
        return "'%s%s'" % (self.elem, self.ioni)

    def _cut(self, llzero, llfin):
        """Keeps only the lines with their llzero <= lambda_ <= llfin."""
        for i in reversed(list(range(len(self)))):
            if not (llzero <= self.lines[i].lambda_ <= llfin):
                del self.lines[i]


@a99.froze_it
class AtomicLine(a99.AttrsPart):
    attrs = ["lambda_", "kiex", "algf", "ch", "gr", "ge", "zinf", "abondr"]

    def __init__(self):
        a99.AttrsPart.__init__(self)

        # all scalars
        self.lambda_ = None
        self.kiex = None
        self.algf = None
        self.ch = None
        self.gr = None
        self.ge = None
        self.zinf = None
        self.abondr = None

    def filter(self, lzero, lfin):
        """Reduces the number of lines to only the ones whose lambda is inside [lzero, lfin]"""
        raise NotImplementedError()


class FileAtoms(DataFile):
    """
    PFANT Atomic Lines
    """

    default_filename = "atoms.dat"
    attrs = ["atoms", "num_lines"]
    editors = ["ated.py"]

    @property
    def llzero(self):
        """Minimum wavelength"""
        return min([a.llzero for a in self.atoms])

    @property
    def llfin(self):
        """Maximum wavelength"""
        return max([a.llfin for a in self.atoms])

    @property
    def num_lines(self):
        ret = sum(map(len, self.atoms))
        return ret

    # Properties that iterate through the AtomicLine objects to mount vectors
    @property
    def lines(self):
        """Merges all AtomicLine objects. Returns a list."""
        ret = []
        for a in self.atoms:
            ret.extend(a.lines)
        return ret
    @property
    def lambda_(self):
        return np.hstack([np.array([x.lambda_ for x in a.lines]) for a in self.atoms])
    @property
    def kiex(self):
        return np.hstack([np.array([x.kiex for x in a.lines]) for a in self.atoms])
    @property
    def algf(self):
        return np.hstack([np.array([x.algf for x in a.lines]) for a in self.atoms])
    @property
    def ch(self):
        return np.hstack([np.array([x.ch for x in a.lines]) for a in self.atoms])
    @property
    def gr(self):
        return np.hstack([np.array([x.gr for x in a.lines]) for a in self.atoms])
    @property
    def ge(self):
        return np.hstack([np.array([x.ge for x in a.lines]) for a in self.atoms])
    @property
    def zinf(self):
        return np.hstack([np.array([x.zinf for x in a.lines]) for a in self.atoms])
    @property
    def abondr(self):
        return np.hstack([np.array([x.abondr for x in a.lines]) for a in self.atoms])

    def __len__(self):
        """Length of FileAtoms object is defined as number of elements."""
        return len(self.atoms)

    def __init__(self):
        DataFile.__init__(self)

        # list of Atom objects
        self.atoms = []

    def __str__(self):
        data = [["{} {}".format(atom.elem, atom.ioni), len(atom)] for atom in self]
        headers = ["Species", "Number of lines"]
        return tabulate.tabulate(data, headers)

    def find_atom(self, search):
        """Returns Atom object given search string such as "Fe1"; may raise ValueError or IndexError"""
        import f311.filetypes as ft
        elem, ioni = ft.str_to_elem_ioni(search)

        for atom in self.atoms:
            if atom.elem == elem and atom.ioni == ioni:
                return atom

        raise IndexError("Cannot find '{}'".format(search))


    def cut(self, llzero, llfin):
        """Keeps only the lines with their llzero <= lambda_ <= llfin."""
        for i in reversed(list(range(len(self)))):
            atom = self.atoms[i]
            atom._cut(llzero, llfin)
            if len(atom) == 0:
                del self.atoms[i]

    def filter(self, function):
        """
        Filters atomic lines for which function(line) is true.

        Args:
            function: callable:

                - receives an AtomicLine object as argument,
                - must return True or False (meaning whether or not you want that atomic line)

        "function" example: ``lambda line: line.algf >= -7``
        """
        for i in reversed(list(range(len(self)))):
            atom = self.atoms[i]
            atom.lines = list(filter(function, atom.lines))
            if len(atom) == 0:
                del self.atoms[i]

    filter_lines = filter

    def filter_atoms(self, function):
        """
        Filters Atom objects for which function(line) is true.

        Args:
          function: receives an Atomic object as argument.
           Example: lambda atom: atom.ioni <= 2
        """
        self.atoms = list(filter(function, self.atoms))

    def remove_element(self, elem):
        """Removes given element (any ionization level)."""
        elem = adjust_atomic_symbol(elem)
        for i in reversed(list(range(len(self)))):
            atom = self.atoms[i]
            if atom.elem == elem:
                del self.atoms[i]


    def __iter__(self):
        return iter(self.atoms)

    def _do_load(self, filename):
        """Clears internal lists and loads from file."""

        with open(filename, "r") as h:

            r = 0 # counts rows of file
            edict = {}  # links atomic symbols with Atom objects created (key is atomic symbol)
            try:
                while True:
                    line = AtomicLine()

                    # (EE)(I) --whitespace-- (float) --ignored...--
                    temp = a99.str_vector(h)
                    elem, s_ioni = temp[0][:-1], temp[0][-1]
                    line.lambda_ = float(temp[1])
                    elem = adjust_atomic_symbol(elem)
                    key = elem+s_ioni  # will gb.py elements by this key
                    if key in edict:
                        a = edict[key]
                    else:
                        a = edict[key] = Atom()
                        a.elem = elem
                        a.ioni = int(s_ioni)
                        self.atoms.append(a)
                    a.lines.append(line)
                    r += 1

                    [line.kiex, line.algf, line.ch, line.gr, line.ge, line.zinf, line.abondr, finrai] = \
                        a99.float_vector(h)
                    r += 1
                    # last element is end-of-file flag "finrai"
                    if finrai == 1:
                        break
            except Exception as e:
                raise type(e)(("Error around %d%s row of file '%s'" %
                               (r+1, a99.ordinal_suffix(r+1), filename))+": "+str(e)).with_traceback(sys.exc_info()[2])

    def _do_save_as(self, filename):
        with open(filename, "w") as h:
            n = len(self.atoms)
            for i, e in enumerate(self.atoms):
                p = len(e)
                for j, a in enumerate(e.lines):
                    finrai = 1 if i == n-1 and j == p-1 else 0
                    a99.write_lf(h, "%2s%1d %10.3f" % (e.elem, e.ioni, a.lambda_))
                    # Writing floating-point numbers with %.7g format creates a more compact
                    # file. In Fortran it is read with '*' format, so it understands as
                    # long as there is a space between numbers.
                    a99.write_lf(h, "%.7g %.7g %.7g %.7g %.7g %.7g %.7g %1d" % \
                             (a.kiex, a.algf, a.ch, a.gr, a.ge, a.zinf, a.abondr, finrai))
                    # old way write_lf(h, "%8.3f %.7g %8.3f %8.3f %8.3f %6.1f %3.1f %1d" % \
                    #     (a.kiex, a.algf, a.ch, a.gr, a.ge, a.zinf, a.abondr, finrai))
