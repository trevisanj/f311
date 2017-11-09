from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
# from a_WState import WState
# import moldb as db
from .a_WFileMolConsts import *
import os
from ..a_XFileMainWindow import *

__all__ = ["XFileMolConsts"]


class XFileMolConsts(XFileMainWindowBase):
    def __init__(self, *args, moldb=None, **kwargs):
        XFileMainWindowBase.__init__(self, *args, **kwargs)
        if moldb is not None:
            self.me.set_moldb(moldb)

    def set_moldb(self, moldb):
        self.me.set_moldb(moldb)

    def _add_stuff(self):

        import f311.filetypes as ft
        import f311.explorer as ex


        me = self.me = WFileMolConsts(self)
        self.tabWidget.addTab(me, "")

        # # Synchronized sequences
        _VVV = ft.FileMolConsts.description
        self.pages.append(ex.MyPage(
         text_tab="{} (Alt+&1)".format(_VVV),
         text_saveas="Save %s as..." % _VVV,
         text_load="Load %s" % _VVV,
         cls_save=ft.FileMolConsts, clss_load=(ft.FileMolConsts,), wild="*.py",
         editor=me
        ))

        self.setWindowTitle("Molecular constants editor")

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


    # # # Override
    # #   ========
    #
    # def _on_me_changed(self):
    #     """Overriden to commit automatically. "(changed)" will not appear
    #
    #     Changes should be committed by the method that executed queries, but it is so easy to
    #     reinforce this... just in case.
    #     """
    #     index = self._get_tab_index()
    #     if index == 0:
    #         self.me.f.get_conn().commit()  # Just in case
    #     else:
    #         self.flags_changed[index] = True
    #         self._update_tab_texts()
