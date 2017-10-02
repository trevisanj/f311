from .. import FilePy
import a99
from collections import defaultdict

__all__ = ["FileConfigConvMol", "ConfigConvMol"]


@a99.froze_it
class ConfigConvMol(dict):
    def __missing__(self, key):
        return None

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, dict.__repr__(self))


@a99.froze_it
class FileConfigConvMol(FilePy):
    """Python source containing 'config_conv = ConfigConv(...)"""

    description = "configuration file for molecular lines conversion GUI"
    default_filename = "configconvmol.py"
    attrs = ["obj"]
    editors = []

    # Name of variable in module
    varname = "ccm"

    def __init__(self):
        FilePy.__init__(self)
        self.obj = ConfigConvMol()

    def _do_load(self, filename):
        module = a99.import_module(filename)
        self._copy_attr(module, self.varname, ConfigConvMol, "obj")

    def _do_save_as(self, filename):
        with open(filename, "w") as h:
            h.write("{}\n"
                    "from f311.filetypes import ConfigConvMol\n"
                    "\n"
                    "{} = {}\n".format(self._get_header(), self.varname, self.obj))
