"""XText: Window to show text; XHTML: window to show HTML."""
__all__ = ["XText", "XHTML"]

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99


################################################################################
class XText(QMainWindow):
    """
    Args:
      parent=None: nevermind
      text: string
    """

    def __init__(self, parent=None, text="", title=""):
        QMainWindow.__init__(self, parent)

        cw = self.centralWidget = QPlainTextEdit()
        cw.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setCentralWidget(cw)
        cw.setReadOnly(True)  # allows copy but not editing
        cw.setFont(a99.MONO_FONT)
        cw.setPlainText(text)

        self.setWindowTitle(title)
        self.setGeometry(0, 0, 800, 600)
        a99.place_center(self)

################################################################################
class XHTML(QMainWindow):
    """
    Args:
      parent=None: nevermind
      html: string
    """

    def __init__(self, parent=None, html="", title=""):
        QMainWindow.__init__(self, parent)

        cw = self.centralWidget = QTextEdit()
        self.setCentralWidget(cw)
        cw.setReadOnly(True)  # allows copy but not editing
        cw.setText(html)

        self.setWindowTitle(title)
        self.setGeometry(0, 0, 800, 600)
        a99.place_center(self)

