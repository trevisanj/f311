from .datafile import DataFile
import a99
import os
import re

__all__ = ["FilePy"]


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

    def _get_magic(self):
        """Returns string to be written as first line of .py file

         **Note** Newline character **not** included"""

        return "# -*- FilePy: {} -*-".format(self.classname)