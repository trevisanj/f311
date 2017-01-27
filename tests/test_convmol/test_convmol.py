import f311.convmol as cm

import a99



def test_MolConversionLog():
    app = a99.get_QApplication()
    w = cm.MolConversionLog()


def test_WDBRegistry():
    app = a99.get_QApplication()
    w = cm.WDBRegistry(a99.XLogMainWindow())


def test_WDBState():
    app = a99.get_QApplication()
    w = cm.WDBState(a99.XLogMainWindow())


# def test_WMolConst():
#     app = a99.get_QApplication()
#     w = cm.WMolConst(a99.XLogMainWindow())
#
#
# def test_WStateConst():
#     app = a99.get_QApplication()
#     w = cm.WStateConst(a99.XLogMainWindow())


def test_XConvMol():
    app = a99.get_QApplication()
    w = cm.XConvMol()


def test_XFileMolDB():
    app = a99.get_QApplication()
    w = cm.XFileMolDB()

