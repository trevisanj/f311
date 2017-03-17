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
    "Nlow", "symlow", "Eup", "vup", "Jup", "Nup", "symup", "gamrad", "mol", "trans0", "trans1", "branch"])
PlezTiOLine.__doc__ = """Represents one Plez molecular line

Field names were maintained as in Plez 'ReadmeTiO' file with slight changes.
"""


class FilePlezTiO(DataFile):
    """
    Plez molecular lines file, TiO format

    Lines are encoded as PlezTiOLine object
    """

    attrs = ["num_lines"]

    @property
    def num_lines(self):
        return len(self)

    def __len__(self):
        return len(self.lines)

    def __init__(self, flag_parse_atoms=True, flag_parse_molecules=True):
        DataFile.__init__(self)

        self.lines = []

    def __iter__(self):
        return iter(self.lines)

    def _do_load(self, filename):
        def strip(s): return str(s).strip()
        def I(x): return str(x)  # Identity
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
                    if len(s) == 0: break  # # EOF: blank line or references section

                    bits = my_struct.unpack_from(s)

                    # print("<<<<<<<<<<<<<<<<<<<<<<< {}".format(bits))
                    # print("<<<<<<<<<<<<<<<<<<<<<<< {}".format(len(bits)))
                    args = [func(x) for func, x in zip(func_map, bits)]
                    # print("<<<<<<<<<<<<<<<<<<<<<<< {}".format(args))


                    line = PlezTiOLine(*args)
                    self.lines.append(line)


                    #           1         2         3         4         5         6         7         8         9        10        11
                    # 01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678
                    #
                    #    lambda_air(A)   gf         Elow(cm-1)  vl  Jl    Nl  syml  Eup(cm-1) vu   Ju    Nu  symu  gamrad    mol trans branch
                    #      3164.8716 0.769183E-11   3459.6228   0   5.0   5.0  0  35047.3396  15   6.0   6.0  0 1.821557E+07|'TiO a f  R    '
                    # 12345678901234                                                                                        | 12345678901234
                    #               1234567890123                                                                           |
                    #                            123456789012                                                               |
                    #                                        1234                                                           |
                    #                                            123456                                                     |
                    #                                                  123456                                               |
                    #                                                        123                                            |
                    #                                                           123456789012                                |
                    #                                                                       1234                            |
                    #                                                                           123456                      |
                    #                                                                                 123456                |
                    #                                                                                       123             |
                    #                                                                                          1234567890123|
                    #                                                                                                       2x
                    #                                                                                                         123 1 1 123456
                    #                                                                                                                       1s/2sx

                    r += 1
                    ii += 1
                    if ii > 1234:
                        a99.get_python_logger().info(
                            "Loading '{}': {}".format(filename, a99.format_progress(r + 1, num_lines)))
                        ii = 0


            except Exception as e:
                raise type(e)(("Error around %d%s row of file '%s'" %
                               (r + 1, a99.ordinal_suffix(r + 1), filename)) + ": " + str(
                    e)).with_traceback(sys.exc_info()[2])


