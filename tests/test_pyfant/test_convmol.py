import f311.pyfant as pf
import a99



def test_MolConversionLog():
    app = a99.get_QApplication()
    w = pf.convmol.MolConversionLog()


def test_WDBRegistry():
    app = a99.get_QApplication()
    w = pf.convmol.WDBRegistry(a99.XLogMainWindow())


def test_WDBState():
    app = a99.get_QApplication()
    w = pf.convmol.WDBState(a99.XLogMainWindow())


# def test_WMolConst():
#     app = a99.get_QApplication()
#     w = pf.convmol.WMolConst(a99.XLogMainWindow())
#
#
# def test_WStateConst():
#     app = a99.get_QApplication()
#     w = pf.convmol.WStateConst(a99.XLogMainWindow())


def test_XConvMol():
    app = a99.get_QApplication()
    w = pf.convmol.XConvMol()


def test_XFileMolDB():
    app = a99.get_QApplication()
    w = pf.convmol.XFileMolDB()

