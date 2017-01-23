import aosss as ao
import a99


def test_WFileSparseCube():
    app = a99.get_QApplication()
    obj = ao.WFileSparseCube(a99.XLogMainWindow())


def test_WFileSpectrumList():
    app = a99.get_QApplication()
    obj = ao.WFileSpectrumList(a99.XLogMainWindow())


def test_WSpectrumCollection():
    app = a99.get_QApplication()
    obj = ao.WSpectrumCollection(a99.XLogMainWindow())


def test_XFileSparseCube():
    app = a99.get_QApplication()
    obj = ao.XFileSparseCube()


def test_XFileSpectrumList():
    app = a99.get_QApplication()
    obj = ao.XFileSpectrumList()


def test_XGroupSpectra():
    app = a99.get_QApplication()
    obj = ao.XGroupSpectra()


def test_XHelpDialog():
    app = a99.get_QApplication()
    obj = ao.XHelpDialog()


def test_XPlotXY():
    app = a99.get_QApplication()
    obj = ao.XPlotXY(ao.SpectrumCollection())


def test_XPlotXYZ():
    app = a99.get_QApplication()
    obj = ao.XPlotXYZ(ao.SpectrumCollection())


def test_XScaleSpectrum():
    app = a99.get_QApplication()
    obj = ao.XScaleSpectrum()


def test_XToScalar():
    app = a99.get_QApplication()
    obj = ao.XToScalar()


def test_XUseSpectrumBlock():
    app = a99.get_QApplication()
    obj = ao.XUseSpectrumBlock()

