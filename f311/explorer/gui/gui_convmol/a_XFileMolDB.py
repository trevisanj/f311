from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
# from a_WState import WState
# import moldb as db
from .a_WFileMolDB import *
import os
from ..a_XFileMainWindow import *

__all__ = ["XFileMolDB"]


class XFileMolDB(XFileMainWindow):
    def _add_stuff(self):
        import f311.filetypes as ft
        import f311.explorer as ex

        me = self.w_moldb = WFileMolDB(self)
        me.changed.connect(self._on_changed)

        # # Synchronized sequences
        self.pages.append(ex.MyPage(
         text_tab=ft.FileMolDB.description,
         cls_save=ft.FileMolDB, clss_load=(ft.FileMolDB,), wild="*.sqlite",
         editor=me, flag_autosave=True
        ))

        self.setWindowTitle("Molecular information database editor")

    def wants_auto(self):
        idx = self.w_source.index
        filename = None
        if idx == 0:
            lines = self.w_hitran.data
            if lines:
                filename = "{}.dat".format(lines["header"]["table_name"])

        if filename is None:
            # Default
            filename = a99.new_filename("mol", "dat")

        self.w_out.value = filename
