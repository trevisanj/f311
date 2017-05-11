"""Widget to choose a spectrum"""

# TODO get rid of this, maybe.


__all__ = ["WChooseSpectrum"]

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
from f311 import filetypes as ft

class WChooseSpectrum(QWidget):
    """
    Editor to choose a spectrum: edit field with "..." button to find in directory

    Arguments:
      parent=None
    """

    # Emitted whenever any value changes
    changed = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # Whether all the values in the fields are valid or not
        self.flag_valid = False
        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False
        self.sp = None # Spectrum object

        # # Central layout
        la = self.centralLayout = QHBoxLayout()
        a99.set_margin(la, 0)
        self.setLayout(la)

        y = self.lineEdit_sp = QLineEdit()
        la.addWidget(y)
        y.setReadOnly(True)
        y.installEventFilter(self)
        y.textEdited.connect(self.on_edited)

        b = self.b23088 = QPushButton("...")
        la.addWidget(b)
        b.clicked.connect(self.b_clicked)
        b.setFixedWidth(30)


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def load(self, x):
        assert isinstance(x, ft.FileSpectrum)
        self.sp = x
        self.__update_from_sp()


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        pass

    def eventFilter(self, obj_focused, event):
        return False

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def on_edited(self):
        pass
        # if self.flag_process_changes:
            # self.__update_f()
            # self.changed.emit()

    def b_clicked(self):
        # index = self.__get_index()
        # editor, text, cls, label, wild = self.editors[index], \
        #                                  self.open_texts[index], self.clss[index], self.labels_fn[index], \
        #                                  self.wilds[index]
        try:
            d = self.sp.filename if self.sp and self.sp.filename is not None else ft.FileSpectrumPfant.default_filename
            new_filename = QFileDialog.getOpenFileName(self, "Cube", d, "*.fits")[0]
            if new_filename:
                sp = ft.load_spectrum(new_filename)
                if not sp:
                    raise RuntimeError("Failed to load '{0!s}'".format(new_filename))
                self.sp = sp
                self.__update_from_sp()
        except Exception as e:
            a99.show_error(str(e))
            raise


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear

    def __update_from_sp(self):
        self.flag_process_changes = False
        try:
            self.lineEdit_sp.setText(self.sp.filename)
        finally:
            self.flag_process_changes = True
