"""FileMAbFwhm class (differential ABundances and FWHMs)"""


__all__ = ["FileMolConsts"]


from .. import FilePy, adjust_atomic_symbol
import importlib
import numpy as np
import a99
from ..molconsts import MolConsts



def check_module(module_name):
    """
    Checks if module can be imported without actually
    importing it

    Source: https://www.blog.pythonlibrary.org/2016/05/27/python-201-an-intro-to-importlib/
    """
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        print('Module: {} not found'.format(module_name))
        return None
    else:
        print('Module: {} can be imported!'.format(module_name))
        return module_spec

@a99.froze_it
class FileMolConsts(FilePy):
    """Python source containing 'fobj = MolConsts(...)"""

    description = "molecular constants"
    default_filename = "molconsts.py"
    attrs = ["molconsts"]
    editors = []


    def __init__(self):
        FilePy.__init__(self)

        self.molconsts = MolConsts()

    # def validate(self):
    #     pass

    def _do_load(self, filename):
        module = a99.import_module(filename)
        self._copy_attr(module, "molconsts", MolConsts)

    def _do_save_as(self, filename):
        with open(filename, "w") as h:
            h.write("{}\nfrom f311.filetypes import MolConsts\n\n"
                    "molconsts = {}".format(self._get_header(), self.molconsts))



