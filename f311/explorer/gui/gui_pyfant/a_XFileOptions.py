"""Main Editor dialog."""

__all__ = ["XFileOptions"]

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from . import a_WFileMain
import os.path
from ._shared import *
import a99
import f311.filetypes as ft
from ..a_XFileMainWindow import *


class XFileOptions(XFileMainWindow):
    def _add_stuff(self):
        import f311.explorer as ex

        e0 = self.w = ex.WOptionsEditor(self)
        e0.changed.connect(self._on_w_changed)
        e0.loaded.connect(self._on_w_loaded)
        self.tabWidget.addTab(e0, "")
        # self.setCentralWidget(self.w)

        CLS_FILE = ft.FileOptions
        WILD = "*.py" if CLS_FILE.default_filename is None else "*"+os.path.splitext(CLS_FILE.default_filename)[1]
        self.pages.append(ex.MyPage(text_tab="File",
                                    cls_save=CLS_FILE, clss_load=(CLS_FILE,), wild=WILD, editor=e0))
        self.setWindowTitle("{} Editor".format(a99.get_obj_doc0(CLS_FILE)))

    def _on_w_loaded(self):
        pass

    def _on_w_changed(self):
        pass
