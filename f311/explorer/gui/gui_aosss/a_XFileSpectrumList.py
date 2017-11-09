__all__ = ["XFileSpectrumList"]


from .a_WFileSpectrumList import *
import a99
import f311.filetypes as ft
from ..a_XFileMainWindow import *


class XFileSpectrumList(XFileMainWindow):
    def _add_stuff(self):
        import f311

        self.setWindowTitle(a99.get_window_title("Spectrum List Editor"))

        ce = self.ce = WFileSpectrumList(self)

        self.pages.append(MyPage(text_tab="FileSpectrumList editor", cls_save=ft.FileSpectrumList,
            clss_load=[ft.FileSpectrumList, ft.FileFullCube]+f311.classes_sp(), wild="*.splist",
            editor=ce))

        # # Adds spectrum collection actions to menu
        self.menuBar().addMenu(self.ce.menu_actions)
