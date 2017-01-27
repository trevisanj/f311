import f311.pyfant as pf
import a99


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

