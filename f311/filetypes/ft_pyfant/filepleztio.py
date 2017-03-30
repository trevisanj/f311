"""Plez atomic or molecular lines file"""

__all__ = ["FilePlezTiO", "PlezTiOLine"]

# from ..gear import *
import sys
import a99
from .. import DataFile
import io
from collections import namedtuple, defaultdict
import struct
import os
import numpy as np

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

# Position
#           1         2         3         4         5         6         7         8         9        10        11
# 01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678
#
#    lambda_air(A)   gf         Elow(cm-1)  vl  Jl    Nl  syml  Eup(cm-1) vu   Ju    Nu  symu  gamrad    mol trans branch
#      3164.8716 0.769183E-11   3459.6228   0   5.0   5.0  0  35047.3396  15   6.0   6.0  0 1.821557E+07 'TiO a f  R    '
#      3164.8764 0.931064E-11   3466.0556   0   6.0   6.0  0  35053.7238  15   7.0   7.0  0 1.818709E+07 'TiO a f  R    '
#      3164.8827 0.609470E-11   3454.2620   0   4.0   4.0  0  35041.8672  15   5.0   5.0  0 1.824816E+07 'TiO a f  R    '




PlezTiOLine = namedtuple("PlezTiOLine", ["lambda_", "gf", "Elow", "vlow", "Jlow",
    "Nlow", "symlow", "Eup", "vup", "Jup", "Nup", "symup", "gamrad", "mol", "state_from", "state_to", "branch"])
PlezTiOLine.__doc__ = """Represents one Plez molecular line

Field names were maintained as in Plez 'ReadmeTiO' file with slight changes.
"""


class FilePlezTiO(DataFile):
    """
    Plez molecular lines file, TiO format

    Lines are encoded as PlezTiOLine object

    Because Plez files are too big, they will be ***filtered upon load** (unfiltered files may take up
    several GB of RAM memory if fully loaded). See arguments list

    Args:
        min_gf=0: minimum gf
        max_J2l=99999: Maximum J" (J lower)
        max_vl=99999: Maximum v' (v upper)
        max_v2l=99999: Maximum v" (v lower)

    Example:

        >>> from f311 import filetypes as ft
        >>> f = ft.FilePlezTiO(min_gf=10**-4, max_J2l=120, max_vl=9, max_v2l=9)
        >>> f.load("linelist_reduced46_all_deltacorr.dat")
        >>> print("Number of lines loaded: {}".format(len(f))
    """

    attrs = ["num_lines"]

    @property
    def num_lines(self):
        return len(self)

    def __len__(self):
        return len(self.lines)

    def __init__(self, min_gf=0, max_J2l=99999, max_vl=99999, max_v2l=99999):
        DataFile.__init__(self)
        self.lines = []
        self.min_gf = min_gf
        self.max_J2l = max_J2l
        self.max_vl = max_vl
        self.max_v2l = max_v2l

    def __iter__(self):
        return iter(self.lines)



    def get_numpy_array(self):
        """Returns a np array with named fields, same names as in PlezTiOLine"""
        dtype = self._get_dtype()
        return np.array(self.lines, dtype=dtype)

    def _get_dtype(self):
        # dtype = [("lambda_", float),
        #          ("gf", float),
        #          ("Elow", float),
        #          ("vlow", int),
        #          ("Jlow", float),
        #          ("Nlow", float),
        #          ("symlow", int),
        #          ("Eup", float),
        #          ("vup", int),
        #          ("Jup", float),
        #          ("Nup", float),
        #          ("symup", int),
        #          ("gamrad", float),
        #          ("mol", '|S3'),
        #          ("state_from", '|S1'),
        #          ("state_to", '|S1'),
        #          ("branch", '|S6'), ]
        dtype = [("lambda_", float),
                 ("gf", float),
                 ("Elow", float),
                 ("vlow", int),
                 ("Jlow", float),
                 ("Nlow", float),
                 ("symlow", int),
                 ("Eup", float),
                 ("vup", int),
                 ("Jup", float),
                 ("Nup", float),
                 ("symup", int),
                 ("gamrad", float),
                 ("mol", '|S3'),
                 ("state_from", '|S1'),
                 ("state_to", '|S1'),
                 ("branch", '|S6'), ]
        return dtype

    def _do_load(self, filename):
        def strip(s): return s.decode("ascii").strip()
        def I(s): return s.decode("ascii")  # Identity
        my_struct = struct.Struct("14s 13s 12s 4s 6s 6s 3s 12s 4s 6s 6s 3s 13s 2x 3s 1x 1s 1x 1s 6s 2x")
        func_map = [float, float, float, int, float, float, int, float, int, float, float, int,
                    float, strip, I, I, strip]

        filesize = os.path.getsize(filename)
        num_lines = float(filesize)/120

        if num_lines != int(num_lines):
            raise RuntimeError("Fractionary number of lines: {}, not a FilePlezTiO".format(num_lines))
        num_lines = int(num_lines)

        with open(filename, "rb") as h:
            try:
                r = 0  # counts rows of file
                ii = 0  # progress feedback auxiliary variable
                while True:
                    s = h.readline()

                    # print(s)
                    # break
                    if len(s) == 0: break  # # EOF: blank line or references section

                    # Filtering part

                    gf = float(s[14:27])
                    J2l = float(s[43:49])
                    vl = int(s[70:74])
                    v2l = int(s[49:53])

                    # gf = float(bits[1])
                    # J2l = float(bits[4])
                    # vl = float(bits[8])
                    # v2l = float(bits[3])

                    # gf = args[1]
                    # J2l = args[4]
                    # vl = args[8]
                    # v2l = args[3]


                    if not (gf >= self.min_gf and J2l <= self.max_J2l and vl <= self.max_vl and v2l <= self.max_v2l):
                        r +=1
                        continue

                    bits = my_struct.unpack_from(s)

                    args = [func(x) for func, x in zip(func_map, bits)]
                    line = PlezTiOLine(*args)
                    self.lines.append(line)
                    r += 1

                    # args = [func(x) for func, x in zip(func_map, bits)]
                    # line = PlezTiOLine(*bits)
                    # self.lines.append(line)



                    #           1         2         3         4         5         6         7         8         9        10        11
                    # 01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678
                    #
                    #    lambda_air(A)   gf         Elow(cm-1)  vl  Jl    Nl  syml  Eup(cm-1) vu   Ju    Nu  symu  gamrad    mol trans branch
                    #      3164.8716 0.769183E-11   3459.6228   0   5.0   5.0  0  35047.3396  15   6.0   6.0  0 1.821557E+07|'TiO a f  R    '
                    # 12345678901234                                                                                        | 12345678901234
                    # 0             1234567890123                                                                           |
                    #               1            123456789012                                                               |
                    #                            2           1234                                                           |
                    #                                        3   123456                                                     |
                    #                                            4     123456                                               |
                    #                                                  5     123                                            |
                    #                                                        6  123456789012                                |
                    #                                                           7           1234                            |
                    #                                                                       8   123456                      |
                    #                                                                           9     123456                |
                    #                                                                                 10    123             |
                    #                                                                                       11 1234567890123|
                    #                                                                                          12           2x
                    #                                                                                                         123 1 1 123456
                    #                                                                                                         13  141516

                    ii += 1
                    if ii > 12345:
                        a99.get_python_logger().info(
                            "Loading '{}': {}".format(filename, a99.format_progress(r + 1, num_lines)))
                        ii = 0


            except Exception as e:
                raise type(e)(("Error around %d%s row of file '%s'" %
                               (r + 1, a99.ordinal_suffix(r + 1), filename)) + ": " + str(
                    e)).with_traceback(sys.exc_info()[2])



    def _do_save_as(self, filename):
        with open(filename, "w") as h:
            for line in self.lines:
               h.write("{:14.4f} {:12e} {:11.4f} {:3d} {:5.1f} {:5.1f} {:2d} {:11.4f} {:3d} {:5.1f} {:5.1f} {:2d} {:12e} '{:3s} {:1s} {:1s} {:6s}'\n".format(*line))
