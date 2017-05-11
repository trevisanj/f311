import f311.convmol as cm
import f311.explorer as ex
import a99



def test_MolConversionLog():
    app = a99.get_QApplication()
    w = cm.MolConversionLog()


def test_WDBRegistry():
    app = a99.get_QApplication()
    w = a99.WDBRegistry(a99.XLogMainWindow())


def test_WMolecularConstants():
    app = a99.get_QApplication()
    w = ex.WMolecularConstants(a99.XLogMainWindow())


# def test_XConvMol():
#     app = a99.get_QApplication()
#     w = cm.XConvMol()


def test_XFileMolDB():
    app = a99.get_QApplication()
    w = ex.XFileMolDB()

