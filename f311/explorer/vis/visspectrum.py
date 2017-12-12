from ... import filetypes as ft
from .basic import Vis
import matplotlib.pyplot as plt


__all__ = ["VisPrint", "VisSpectrum"]


class VisPrint(Vis):
    """Prints object to screen."""

    input_classes = (object,)
    action = "Print to console"

    def _do_use(self, obj):
        print(obj)


class VisSpectrum(Vis):
    """Plots single spectrum."""

    input_classes = (ft.FileSpectrum,)
    action = "Plot spectrum"

    def _do_use(self, m):
        from f311 import explorer as ex
        s = m.spectrum
        ex.plot_spectra_stacked([s])

