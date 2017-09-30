"""Widget to edit a FileMain object."""

__all__ = ["WFileMolConsts"]

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
import f311.filetypes as ft
from .a_WMolecularConstants import *


class WFileMolConsts(a99.WEditor):
    """
    FileMolConsts editor widget.

    Args:
      parent=None
    """

    # Emitted whenever any value changes
    changed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        a99.WEditor.__init__(self, *args, **kwargs)

        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False


        # # Central layout
        l = self.centralLayout = QVBoxLayout()
        a99.set_margin(l, 0)
        self.setLayout(l)

        la = self.label_fn = QLabel()
        l.addWidget(la)

        w = self.w_molconsts = WMolecularConstants(self.parent_form)
        w.changed.connect(self._on_w_molconsts_changed)
        l.addWidget(w)


        self.setEnabled(False)  # disabled until load() is called
        self.flag_process_changes = True


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def set_moldb(self, fobj):
        self.w_molconsts.set_moldb(fobj)

    def _do_load(self, fobj):
        assert isinstance(fobj, ft.FileMolConsts)
        self._f = fobj
        self.w_molconsts.molconsts = fobj.molconsts
        # self.w_molconsts.f = fobj.molconsts
        # self.__update_gui()
        self.setEnabled(True)
        self._flag_valid = True

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        """Sets focus to first field. Note: reason is ignored."""
        self.w_molconsts.setFocus()


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def _on_w_molconsts_changed(self):
        if self.flag_process_changes:
            self._flag_valid = self.w_molconsts.flag_valid
            self.changed.emit()

