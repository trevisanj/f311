import f311.pyfant as pf
import a99


def test_WFileAbXFwhm():
    app = a99.get_QApplication()
    w = pf.WFileAbXFwhm()


def test_WFileAbonds():
    app = a99.get_QApplication()
    w = pf.WFileAbonds()


def test_WFileMain():
    app = a99.get_QApplication()
    w = pf.WFileMain()


def test_WOptionsEditor():
    app = a99.get_QApplication()
    w = pf.WOptionsEditor()



def test_XFileAbonds():
    app = a99.get_QApplication()
    w = pf.XFileAbonds()


def test_XFileAtoms():
    app = a99.get_QApplication()
    w = pf.XFileAtoms()


def test_XFileMain():
    app = a99.get_QApplication()
    w = pf.XFileMain()


def test_XFileMolecules():
    app = a99.get_QApplication()
    w = pf.XFileMolecules()


def test_XMainAbonds():
    app = a99.get_QApplication()
    w = pf.XMainAbonds()


def test_XMulti():
    app = a99.get_QApplication()
    w = pf.XMulti()


def test_XPFANT():
    app = a99.get_QApplication()
    w = pf.XPFANT()


def test_XRunnableManager():
    app = a99.get_QApplication()
    rm = pf.RunnableManager()
    w = pf.XRunnableManager(None, rm)


def test_XMolLinesEditor():
    app = a99.get_QApplication()
    w = pf.XMolLinesEditor(None)


def test_XFileAtomsHistogram():
    app = a99.get_QApplication()
    w = pf.XFileAtomsHistogram(None)

def test_XAtomLinesEditor():
    app = a99.get_QApplication()
    w = pf.XAtomLinesEditor(None)

