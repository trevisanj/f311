from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from a99 import WDBRegistry
import a99
from .a_WDBFCF import *
from .a_WDBSystem import *

__all__ = ["WDBSystemFCF"]


class WDBSystemFCF(a99.WBase):
    """Master-slave widget to lodge System and FCF widgets"""

    # Emitted whenever the value of the 'id' property changes
    id_changed = pyqtSignal()

    @property
    def id(self):
        """System id or None"""
        return self.w_system._get_id()

    @property
    def f(self):
        """Object representing the file being edited (possibly a DataFile object)"""
        return self._f

    @f.setter
    def f(self, f):
        self.w_system.f = f
        self.w_fcf.f = f

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        # # Main layout & splitter
        lmain = self.keep_ref(QVBoxLayout(self))
        sp = self.keep_ref(QSplitter(Qt.Horizontal))


        # ## First widget of splitter
        w0 = self.keep_ref(QWidget())
        l0 = QVBoxLayout(w0)
        a99.set_margin(l0, 0)
        l0.setSpacing(2)

        a = self.title_mol = QLabel(a99.format_title1("Systems"))
        l0.addWidget(a)

        w = self.w_system = WDBSystem(self.parent_form)
        w.id_changed.connect(self.id_system_changed)
        w.id_changed.connect(self.id_changed)
        w.changed.connect(self.changed)
        l0.addWidget(w)

        # ## Second widget of splitter
        w1 = self.keep_ref(QWidget())
        l1 = QVBoxLayout(w1)
        a99.set_margin(l1, 0)
        l1.setSpacing(2)

        a = self.title_state = self.keep_ref(QLabel(a99.format_title1("Franck-Condon Factors")))
        l1.addWidget(a)

        w = self.w_fcf = WDBFCF(self.parent_form)
        w.changed.connect(self.changed)
        l1.addWidget(w)

        sp.addWidget(w0)
        sp.addWidget(w1)
        lmain.addWidget(sp)

        # # Final adjustments
        a99.nerdify(self)


    def set_id_molecule(self, id_):
        """Propagates to self.w_system"""
        self.w_system.set_id_molecule(id_)
        # self._populate()

    def id_system_changed(self):
        self.w_fcf.set_id_system(self.w_system.id)
