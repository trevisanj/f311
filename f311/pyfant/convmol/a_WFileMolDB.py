from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
from .a_WDBMolecule import WDBMolecule
from .a_WDBState import WDBState
import os


__all__ = ["WFileMolDB"]


class WFileMolDB(a99.WBase):

    @property
    def f(self):
        return self._f

    # @f.setter
    # def f(self, x):
    #     self._f = x
    #     self.w_mol.f = x
    #     self.w_state.f = x

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        self._f = None
        self.flag_valid = True  # To keep XFileMainWindow happy

        # # Main layout & splitter
        lmain = self.keep_ref(QVBoxLayout(self))
        sp = self.keep_ref(QSplitter(Qt.Vertical))


        # ## Line showing the File Name
        l1 = self.keep_ref(QHBoxLayout())
        lmain.addLayout(l1)
        a99.set_margin(l1, 0)
        l1.addWidget(self.keep_ref(QLabel("<b>File:<b>")))
        w = self.label_fn = QLabel()
        l1.addWidget(w)
        l1.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))


        # ## First widget of splitter
        w0 = self.keep_ref(QWidget())
        l0 = QVBoxLayout(w0)
        a99.set_margin(l0, 2)
        l0.setSpacing(2)

        a = self.title_mol = QLabel(a99.format_title0("Select a molecule:"))
        l0.addWidget(a)

        w = self.w_mol = WDBMolecule(self.parent_form)
        w.layout().setContentsMargins(15, 1, 1, 1)
        w.id_changed.connect(self.mol_id_changed)
        l0.addWidget(w)

        # ## Second widget of splitter
        w1 = self.keep_ref(QWidget())
        l1 = QVBoxLayout(w1)
        a99.set_margin(l1, 2)
        l1.setSpacing(2)

        a = self.title_state = self.keep_ref(QLabel(a99.format_title0("States")))
        l1.addWidget(a)

        w = self.w_state = WDBState(self.parent_form)
        w.layout().setContentsMargins(15, 1, 1, 1)
        l1.addWidget(w)

        sp.addWidget(w0)
        sp.addWidget(w1)
        lmain.addWidget(sp)

        # # Final adjustments
        a99.nerdify(self)

    def load(self, x):
        self._f = x
        self.w_mol.f = x
        self.w_state.f = x
        self.update_gui_label_fn()


    def mol_id_changed(self):
        id_ = self.w_mol.id
        row = self.w_mol.row
        self.w_state.set_id_molecule(id_)
        s = "States (no molecule selected)" if not row else "Select a State for molecule '{}'".format(
            row["formula"])
        self.title_state.setText(a99.format_title0(s))


    # # Override
    #   ========

    def update_gui_label_fn(self):
        if not self._f:
            text = "(not loaded)"
        elif self._f.filename:
            text = os.path.relpath(self._f.filename, ".")
        else:
            text = "(filename not set)"
        self.label_fn.setText(text)
