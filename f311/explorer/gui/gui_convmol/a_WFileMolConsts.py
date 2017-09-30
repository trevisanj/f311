"""Widget to edit a FileMain object."""

__all__ = ["WFileMolConsts"]

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
import f311.filetypes as ft
from .a_WMolecularConstants import *


class WFileMolConsts(a99.WBase):
    """
    FileMolConsts editor widget.

    Args:
      parent=None
    """

    # Emitted whenever any value changes
    changed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        a99.WBase.__init__(self, *args, **kwargs)
        # Whether all the values in the fields are valid or not
        self.flag_valid = False
        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False
        self.f = None # FileMolConsts object


        # # Central layout
        l = self.centralLayout = QVBoxLayout()
        a99.set_margin(l, 0)
        self.setLayout(l)

        w = self.w_molconsts = WMolecularConstants(self.parent_form)
        l.addWidget(w)


        self.setEnabled(False)  # disabled until load() is called
        self.flag_process_changes = True


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def load(self, x):
        assert isinstance(x, ft.FileMolConsts)
        self.f = x
        self.w_molconsts.f = x.mol_consts
        self.__update_gui()
        self.setEnabled(True)
        self.flag_valid = True

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        """Sets focus to first field. Note: reason is ignored."""
        self.w_molconsts.setFocus()


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def on_edited(self):
        if self.flag_process_changes:
            self.__update_f()
            self.changed.emit()


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear

    def __update_gui(self):
        self.flag_process_changes = False
        try:
            o = self.f
            # self.lineEdit_titrav.setText(o.titrav)
        finally:
            self.flag_process_changes = True

    def __update_f(self):
        self.f.mol_consts = self.w_molconsts.constants
        self.flag_valid = True
