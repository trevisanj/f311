import datetime
from .datafile import DataFile
import a99
import re

__all__ = ["FilePy", "ConfigDict", "FilePyConfig"]


@a99.froze_it
class ConfigDict(dict):
    """Data class to store config options as dictionary"""
    def __missing__(self, key):
        return None

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, dict.__repr__(self))


class FilePy(DataFile):
    """
    Configuration file saved as a .py Python source script

    This class is not intendend to be instantialized. It is an ancestor class for other classes.
    """

    def _test_magic(self, filename):
        with open(filename, "r") as file:
            line = file.readline()
            if not re.match("\s*#\s*-\*-\s*FilePy:\s*{}\s*-\*-".format(self.classname), line):
                raise RuntimeError("File '{}' does not appear to be a '{}' (expected first line of code:"
                                   " \"{}\")".format(filename, self.classname, self._get_magic()))

    def _get_header(self):
        """
        Returns string to be at top of file"""

        return "{}\n#\n# @ Now @ {}\n#\n".format(self._get_magic(), datetime.datetime.now())


    def _get_magic(self):
        """
        Returns string to be written the first line of .py file

        **Note** Newline character **not** included
        """

        return "# -*- FilePy: {} -*-".format(self.classname)

    def _copy_attr(self, module, varname, cls, attrname=None):
        """
        Copies attribute from module object to self. Raises if object not of expected class

        Args:
            module: module object
            varname: variable name
            cls: expected class of variable
            attrname: attribute name of self. Falls back to varname
        """

        if not hasattr(module, varname):
            raise RuntimeError("Variable '{}' not found".format(varname))

        obj = getattr(module, varname)

        if not isinstance(obj, cls):
            raise RuntimeError(
                "Expecting fobj to be a {}, not a '{}'".format(cls.__name__, obj.__class__.__name__))

        if attrname is None:
            attrname = varname

        setattr(self, attrname, obj)



class FilePyConfig(FilePy):
    """Base class for config files. Inherit and set class variable 'modulevarname' besides usual"""

    attrs = ["obj"]

    # Name of variable in module
    modulevarname = "obj"

    def __init__(self):
        FilePy.__init__(self)
        self.obj = ConfigDict()

    def _do_load(self, filename):
        module = a99.import_module(filename)
        self._copy_attr(module, self.modulevarname, ConfigDict, "obj")

    def _do_save_as(self, filename):
        with open(filename, "w") as h:
            h.write("{}\n"
                    "from f311.filetypes import ConfigDict\n"
                    "\n"
                    "{} = {}\n".format(self._get_header(), self.modulevarname, a99.make_code_readable(repr(self.obj))))

    def init_default(self):
        # Already created OK
        pass
