from .. import FilePy
import a99
from ..molconsts import MolConsts

__all__ = ["FileMolConsts"]

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
