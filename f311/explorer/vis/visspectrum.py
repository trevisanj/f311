import a99
from .visbase import Vis


__all__ = ["VisPrint", "VisSpectrum"]


class VisPrint(Vis):
    """Prints object to screen."""

    input_classes = (object,)
    action = "Print to console"

    def _do_use(self, obj):
        print(obj)


class VisSpectrum(Vis):
    """Plots single spectrum."""

    input_classes = (a99.FileSpectrum,)
    action = "Plot spectrum"

    def _do_use(self, m):
        s = m.spectrum
        a99.plot_spectra([s])

