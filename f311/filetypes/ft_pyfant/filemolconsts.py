"""FileMAbFwhm class (differential ABundances and FWHMs)"""


__all__ = ["FileMolConsts"]


from .. import FilePy, adjust_atomic_symbol
import imp
import numpy as np
import a99
from ..molconsts import MolConsts


_COMMENT0 = """# Specification of differential abundances for each chemical.
# Differential abundance is a number to add to original value in abonds.dat.
# All lists of abundances for each element must have the same length."""
_COMMENT1 = """# Name for each pfant run. They will be part of spectrum file names.
# This is optional. If not used, sequential numbers will be used instead.
# Example: pfant_names = ["A", "B", "C", "D"]"""
_COMMENT2 = """# Convolutions specification for fwhm parameter:
# [first value, last value, step]"""


@a99.froze_it
class FileMolConsts(FilePy):
    __doc__ = """`x.py` Differential Abundances and FWHMs (Python source)

This file is actually Python source. Here is a sample:

%s
ab = {"Ca": [-.3, 0, .3, .5],
      "Si": [-.3, 0, .3, .5]}

%s
pfant_names = []

%s
conv = [0.08, 0.6,  0.04]
""" % (_COMMENT0, _COMMENT1, _COMMENT2)


    description = "abundances X FWHM's"
    default_filename = "abxfwhm.py"
    attrs = ["ab", "conv"]
    editors = ["x.py"]

    @property
    def ab(self):
        """Abundances dictionary.

        Setting this property will cause source to be rebuilt and comments to
        be lost."""
        return self.__ab

    @ab.setter
    def ab(self, x):
        self.__ab = x
        self.__adjust_atomic_symbols()
        self.__rebuild_source()

    @property
    def conv(self):
        """Convolutions FWHM list.

        Setting this property will cause source to be rebuilt and comments to
        be lost."""
        return self.__conv

    @conv.setter
    def conv(self, x):
        self.__conv = x
        self.__rebuild_source()

    @property
    def pfant_names(self):
        """List of "names" for each pfant run.

        Must be empty or be of same size as any list of self.ab"""
        return self.__pfant_names

    @pfant_names.setter
    def pfant_names(self, x):
        self.__pfant_names = x


    @property
    def source(self):
        """Source code.

        Better to set this property than to set ab/conv. Setting this property
        will preserve the source code, whereas setting ab/conv separately will
        cause the source code to be rebuilt and become as boring as possible.
        """
        return self.__source

    @source.setter
    def source(self, x):
        self.__parse(x)

    def __init__(self):
        FilePy.__init__(self)

        self.mol_consts = MolConsts()

    def validate(self):
        pass

    def __parse(self, x):
        """Populates __ab, __conf, and __source."""
        cfg = imp.new_module('cfg')
        exec(x, cfg.__dict__)
        if "data" not in cfg.__dict__:
            raise RuntimeError("'data' variable not found")

        data = dict(cfg.data)
        for key, value in data.items():
            if key not in self.mol_consts._KEYS:
                a99.get_python_logger().info("Skipped unknown key '{}'".format(key))
            else:
                self.mol_consts[key] = value


    def _do_load(self, filename):
        with open(filename, "r") as h:
            self.__parse(h.read())

    def _do_save_as(self, filename):
        with open(filename, "w") as h:
            h.write("data = {}".format(dict(self.mol_consts)))

