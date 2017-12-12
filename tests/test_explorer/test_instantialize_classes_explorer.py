import f311.explorer as ex
import a99
from astropy import units as u


def test_PlotSpectrumSetup():
    _ = ex.PlotSpectrumSetup()


def test_XExplorer():
    app = a99.get_QApplication()
    form = ex.XExplorer(_flag_set_dir=False)

def test_XHTML():
    app = a99.get_QApplication()
    _ = ex.XHTML()


def test_XText():
    app = a99.get_QApplication()
    _ = ex.XText()

