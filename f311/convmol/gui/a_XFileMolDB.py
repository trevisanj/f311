from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
# from a_WState import WState
# import moldb as db
from .a_WFileMolDB import *
import os
import f311.filetypes as ft


__all__ = ["XFileMolDB"]


class XFileMolDB(a99.XFileMainWindow):
    def __init__(self, parent=None, fileobj=None):
        a99.XFileMainWindow.__init__(self, parent)

        # # Synchronized sequences
        _VVV = ft.FileMolDB.description
        self.tab_texts[0] =  "{} (Alt+&1)".format(_VVV)
        self.tabWidget.setTabText(0, self.tab_texts[0])
        self.save_as_texts[0] = "Save %s as..." % _VVV
        self.open_texts[0] = "Load %s" % _VVV
        self.clss[0] = ft.FileMolDB
        self.clsss[0] = (ft.FileMolDB,)
        self.wilds[0] = "*.sqlite"


        lv = self.keep_ref(QVBoxLayout(self.gotting))
        me = self.moldb_editor = WFileMolDB(self)
        lv.addWidget(me)
        me.edited.connect(self._on_edited)
        self.editors[0] = me


        if fileobj is not None:
            self.load(fileobj)

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


    def on_fill_missing(self):
        self.w_mol.None_to_zero()
        self.w_state.None_to_zero()

    # def mol_id_changed(self):
    #     id_ = self.w_mol.w_mol.id
    #     row = self.w_mol.w_mol.row
    #     self.w_state.set_id_molecule(id_)
    #     s = "States (no molecule selected)" if not row else "Select a State for molecule '{}'".format(row["formula"])
    #     self.title_state.setText(a99.format_title0(s))


    # # Override
    #   ========
