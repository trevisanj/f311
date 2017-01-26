# #
# #
# # b
# # For OH, the format of branch (Br) in the lower-state quanta field is 2A1 to accommodate the total orbital angular
# # momentum N as well as J
# #
# #
# #
# # References:
# # [1] Rothman, Laurence S., et al. "The HITRAN 2004 molecular spectroscopic database."
# #     Journal of Quantitative Spectroscopy and Radiative Transfer 96.2 (2005): 139-204.
#
#
#
# __all__ = ["FileHitran", "Atom", "HitranLine"]
#
# import pyfant as pf
# import hapi
# from ..misc import *
# from ..errors import *
# import struct
# import logging
# import sys
# import numpy as np
#
# _logger = logging.getLogger(__name__)
# _logger.addHandler(logging.NullHandler())
#
#
# class FileHitran(DataFile):
#     """
#     PFANT Atomic Lines
#     """
#
#     default_filename = "Hitran.dat"
#     attrs = ["Hitran", "num_lines"]
#
#     @property
#     def num_lines(self):
#         ret = sum(map(len, self.Hitran))
#         return ret
#
#     # Properties that iterate through the HitranLine objects to mount vectors
#     @property
#     def lines(self):
#         """Merges all HitranLine objects. Returns a list."""
#         ret = []
#         for a in self.Hitran:
#             ret.extend(a.lines)
#         return ret
#     @property
#     def lambda_(self):
#         return np.hstack([np.array([x.lambda_ for x in a.lines]) for a in self.Hitran])
#     @property
#     def kiex(self):
#         return np.hstack([np.array([x.kiex for x in a.lines]) for a in self.Hitran])
#     @property
#     def algf(self):
#         return np.hstack([np.array([x.algf for x in a.lines]) for a in self.Hitran])
#     @property
#     def ch(self):
#         return np.hstack([np.array([x.ch for x in a.lines]) for a in self.Hitran])
#     @property
#     def gr(self):
#         return np.hstack([np.array([x.gr for x in a.lines]) for a in self.Hitran])
#     @property
#     def ge(self):
#         return np.hstack([np.array([x.ge for x in a.lines]) for a in self.Hitran])
#     @property
#     def zinf(self):
#         return np.hstack([np.array([x.zinf for x in a.lines]) for a in self.Hitran])
#     @property
#     def abondr(self):
#         return np.hstack([np.array([x.abondr for x in a.lines]) for a in self.Hitran])
#
#     def __len__(self):
#         """Length of FileHitran object is defined as number of elements."""
#         return len(self.Hitran)
#
#     def __init__(self):
#         DataFile.__init__(self)
#
#         # list of Atom objects
#         self.Hitran = []
#
#     def cut(self, llzero, llfin):
#         """Keeps only the lines with their llzero <= lambda_ <= llfin."""
#         for i in reversed(list(range(len(self)))):
#             atom = self.Hitran[i]
#             atom._cut(llzero, llfin)
#             if len(atom) == 0:
#                 del self.Hitran[i]
#
#     def filter(self, function):
#         """
#         Filters atomic lines for which function(line) is true.
#
#         Arguments:
#           function -- receives an HitranLine object as argument.
#            Example: lambda line: line.algf >= -7
#         """
#         for i in reversed(list(range(len(self)))):
#             atom = self.Hitran[i]
#             atom.lines = list(filter(function, atom.lines))
#             if len(atom) == 0:
#                 del self.Hitran[i]
#
#     filter_lines = filter
#
#     def filter_Hitran(self, function):
#         """
#         Filters Atom objects for which function(line) is true.
#
#         Arguments:
#           function -- receives an Atomic object as argument.
#            Example: lambda atom: atom.ioni <= 2
#         """
#         self.Hitran = list(filter(function, self.Hitran))
#
#     def remove_element(self, elem):
#         """Removes given element (any ionization level)."""
#         elem = adjust_atomic_symbol(elem)
#         for i in reversed(list(range(len(self)))):
#             atom = self.Hitran[i]
#             if atom.elem == elem:
#                 del self.Hitran[i]
#
#
#     def _do_load(self, filename):
#         """Clears internal lists and loads from file."""
#
#         with open(filename, "r") as h:
#
#             r = 0 # counts rows of file
#             edict = {}  # links atomic symbols with Atom objects created (key is atomic symbol)
#             try:
#                 while True:
#                     line = HitranLine()
#
#                     # (EE)(I) --whitespace-- (float) --ignored...--
#                     temp = str_vector(h)
#                     elem, s_ioni = temp[0][:-1], temp[0][-1]
#                     line.lambda_ = float(temp[1])
#                     elem = adjust_atomic_symbol(elem)
#                     key = elem+s_ioni  # will gb.py elements by this key
#                     if key in edict:
#                         a = edict[key]
#                     else:
#                         a = edict[key] = Atom()
#                         a.elem = elem
#                         a.ioni = int(s_ioni)
#                         self.Hitran.append(a)
#                     a.lines.append(line)
#                     r += 1
#
#                     [line.kiex, line.algf, line.ch, line.gr, line.ge, line.zinf, line.abondr, finrai] = \
#                         float_vector(h)
#                     r += 1
#                     # last element is end-of-file flag "finrai"
#                     if finrai == 1:
#                         break
#             except Exception as e:
#                 raise type(e)(("Error around %d%s row of file '%s'" %
#                                (r+1, ordinal_suffix(r+1), filename))+": "+str(e)).with_traceback(sys.exc_info()[2])
#
#     def _do_save_as(self, filename):
#         with open(filename, "w") as h:
#             n = len(self.Hitran)
#             for i, e in enumerate(self.Hitran):
#                 p = len(e)
#                 for j, a in enumerate(e.lines):
#                     finrai = 1 if i == n-1 and j == p-1 else 0
#                     write_lf(h, "%2s%1d %10.3f" % (e.elem, e.ioni, a.lambda_))
#                     # Writing floating-point numbers with %.7g format creates a more compact
#                     # file. In Fortran it is read with '*' format, so it understands as
#                     # long as there is a space between numbers.
#                     write_lf(h, "%.7g %.7g %.7g %.7g %.7g %.7g %.7g %1d" % \
#                              (a.kiex, a.algf, a.ch, a.gr, a.ge, a.zinf, a.abondr, finrai))
#                     # old way write_lf(h, "%8.3f %.7g %8.3f %8.3f %8.3f %6.1f %3.1f %1d" % \
#                     #     (a.kiex, a.algf, a.ch, a.gr, a.ge, a.zinf, a.abondr, finrai))
