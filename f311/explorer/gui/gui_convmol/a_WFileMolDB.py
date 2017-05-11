from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
from .a_WDBMolecule import WDBMolecule
from .a_WDBState import WDBState
from .a_WDBPFANTMol import *
from .a_WDBSystemFCF import *
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
        a99.set_margin(lmain, 0)
        sp = self.splitter_bidon = QSplitter(Qt.Horizontal)

        # ## Line showing the File Name
        l1 = self.keep_ref(QHBoxLayout())
        lmain.addLayout(l1)
        a99.set_margin(l1, 0)
        v = self.keep_ref(QLabel("<b>File:<b>"))
        v.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l1.addWidget(v)
        w = self.label_fn = QLabel()
        w.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        l1.addWidget(w)
        l1.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))


        # ## First widget of splitter: molecules
        w0 = self.keep_ref(QWidget())
        l0 = QVBoxLayout(w0)
        a99.set_margin(l0, 2)
        l0.setSpacing(2)

        a = self.title_mol = QLabel(a99.format_title0("Molecules (Alt+&4)"))
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

        # ### First tab: molecule headers frmo PFANT molecular lines file
        w = self.w_pfantmol = WDBPFANTMol(self.parent_form)
        w.changed.connect(self.changed)
        w1.addTab(self.w_pfantmol, "PFANT molecules (Alt+&P)")
        # a99.set_margin(w10, 0)

        # ### Second tab: systems and Franck-Condon factors
        w = self.w_system = WDBSystemFCF(self.parent_form)
        w.changed.connect(self.changed)
        w1.addTab(self.w_system, "Electronic systems (Alt+&E)")

        # ### Thirs tab: NIST Chemistry Web Book data
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

    def load(self, x):
        self._f = x
        self.w_mol.f = x
        self.w_state.f = x
        self.w_pfantmol.f = x
        self.w_system.f = x
        self.update_gui_label_fn()


    def mol_id_changed(self):
        id_ = self.w_mol.id
        row = self.w_mol.row
        self.w_pfantmol.set_id_molecule(id_)
        self.w_state.set_id_molecule(id_)
        self.w_system.set_id_molecule(id_)


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
