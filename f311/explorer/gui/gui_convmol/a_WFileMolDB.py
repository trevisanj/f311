from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
from .a_WDBMolecule import WDBMolecule
from .a_WDBState import WDBState
from .a_WDBSystemPfantmolFCF import *
import os


__all__ = ["WFileMolDB"]


class WFileMolDB(a99.WEditor):


    def __init__(self, *args):
        a99.WEditor.__init__(self, *args)

        # # Main layout & splitter
        lmain = self.layout_editor

        sp = self.splitter_bidon = QSplitter(Qt.Horizontal)

        # ## First widget of splitter: molecules
        w0 = self.keep_ref(QWidget())
        l0 = QVBoxLayout(w0)
        a99.set_margin(l0, 2)
        l0.setSpacing(2)

        a = self.title_mol = QLabel(a99.format_title0("Molecules (Alt+&M)"))
        l0.addWidget(a)

        w = self.keep_ref(QLineEdit())
        l0.addWidget(w)

        w = self.w_mol = WDBMolecule(self.parent_form)
        # **Note** Cannot set buddy to w itself because it has a Qt.NoFocus policy
        a.setBuddy(w.tableWidget)
        w.id_changed.connect(self.mol_id_changed)
        w.changed.connect(self.changed)
        l0.addWidget(w)

        # ## Second widget of splitter: tab widget containing the rest
        w1 = self.tabWidget = QTabWidget(self)

        # ### First tab: systems, PFANT molecules, and Franck-Condon factors
        w = self.w_system = WDBSystemPFANTMolFCF(self.parent_form)
        w.changed.connect(self.changed)
        w1.addTab(self.w_system, "Electronic systems (Alt+&E)")

        # ### Second tab: NIST Chemistry Web Book data
        w = self.w_state = WDBState(self.parent_form)
        w.changed.connect(self.changed)
        w1.addTab(self.w_state, "States from NIST (Alt+&S)")

        sp.addWidget(w0)
        sp.addWidget(w1)
        # sp.setStretchFactor(0, 1)
        # sp.setStretchFactor(1, 2)

        lmain.addWidget(sp)

        # # Final adjustments
        a99.nerdify(self)

    def load(self, fobj):
        a99.WEditor.load(self, fobj)
        self.w_mol._move_to_first()

    def _do_load(self, fobj):
        self._f = fobj
        self.w_mol.f = fobj
        self.w_system.f = fobj
        self.w_state.f = fobj

    def mol_id_changed(self):
        id_ = self.w_mol.id
        row = self.w_mol.row
        self.w_system.set_id_molecule(id_)
        self.w_state.set_id_molecule(id_)


