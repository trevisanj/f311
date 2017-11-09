__ll__ = ["XFileSparseCube"]

from .a_WFileSparseCube import *
import a99
import f311.filetypes as ft
from ..a_XFileMainWindow import *


class XFileSparseCube(XFileMainWindow):

    def _add_stuff(self):
        self.setWindowTitle(a99.get_window_title("Data Cube Editor"))

        ce = self.ce = WFileSparseCube(self)

        self.pages.append(MyPage(text_tab="FileSparseCube editor",
         cls_save=ft.FileSparseCube, clss_load=(ft.FileSparseCube, ft.FileFullCube), wild="*.fits", editor=ce))

