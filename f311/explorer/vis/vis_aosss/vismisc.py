import a99
from ..basic import Vis
import f311.filetypes as ft


__all__ = ["VisCube", "VisSpectrumList"]


class VisCube(Vis):
    """Opens the Data Cube Editor window."""
    input_classes = (ft.FileFullCube, ft.FileSparseCube)
    action = "Edit using Data Cube Editor"

    def _do_use(self, r):
        from f311 import explorer as ex
        form = a99.keep_ref(ex.XFileSparseCube(self.parent_form, r))
        form.show()


class VisSpectrumList(Vis):
    """Opens the Spectrum List Editor window."""
    input_classes = (ft.FileSpectrumList, ft.FileSpectrum)
    action = "Edit using Spectrum List Editor"

    def _do_use(self, r):
        from f311 import explorer as ex
        form = a99.keep_ref(ex.XFileSpectrumList(self.parent_form, r))
        form.show()
