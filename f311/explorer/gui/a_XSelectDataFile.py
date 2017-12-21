from collections import OrderedDict
import a99
import f311
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

__all__ = ["XSelectDataFile"]

################################################################################
class XSelectDataFile(QDialog):
    """Window to select a DataFile descendant"""

    @property
    def cls(self):
        return self._cls

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        # Class selected
        self._cls = None

        self._add_stuff()

        self._data = f311.get_filetypes_info(editor_quote="'", flag_leaf=True)
        # builds search strings for filter
        for row in self._data:
            row["search"] = "/".join((str(x).upper() for x in row.values()))

        self._populate()

        a99.nerdify(self)
        a99.place_center(self, 800, 600)
        self.setWindowTitle("Select class")


    def _add_stuff(self):
        # # Main layout
        lmain = self.layout_main = a99.keep_ref(QVBoxLayout(self))

        # ## Toolbar: checkboxes with executables
        l1 = self.layout_filter = QHBoxLayout()
        lmain.addLayout(l1)

        w = self.label_filter = QLabel("<b>Fil&ter:</b>")
        l1.addWidget(w)
        w = self.lineEdit_filter = QLineEdit()
        self.label_filter.setBuddy(w)
        w.textEdited.connect(self._on_filter)
        l1.addWidget(w)
        # w.setFixedWidth(100)
        l1.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))


        a = self.tableWidget = QTableWidget()
        lmain.addWidget(a)
        a.setSelectionMode(QAbstractItemView.SingleSelection)
        a.setSelectionBehavior(QAbstractItemView.SelectRows)
        a.setEditTriggers(QTableWidget.NoEditTriggers)
        a.setAlternatingRowColors(True)
        a.currentCellChanged.connect(self._on_tableWidget_currentCellChanged)
        a.itemDoubleClicked.connect(self._close_on_double_click)

        # button box with OK and Cancel buttons
        bb = a99.keep_ref(QDialogButtonBox())
        bb.setOrientation(Qt.Horizontal)
        bb.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        lmain.addWidget(bb)
        bb.rejected.connect(self.reject)
        bb.accepted.connect(self.accept)


    def _on_tableWidget_currentCellChanged(self):
        idx = self.tableWidget.currentRow()
        self._cls = self._data[idx]["class"]

    def _on_filter(self):
        text = self.lineEdit_filter.text().upper()
        flag_filter = len(text) > 0
        for i, row in enumerate(self._data):
            self.tableWidget.setRowHidden(i, flag_filter and text not in row["search"])

    def _close_on_double_click(self):
        self.accept()

    def _populate(self):
        map = OrderedDict([("classname", "Class name"),
                           ("description", "Description"),
                           ("txtbin", "Text/binary"),
                           ("default_filename", "Default filename"),
                           ("editors", "Editors")])

        nr, nc = len(self._data), len(map)
        t = self.tableWidget
        a99.reset_table_widget(t, nr, nc)
        t.setHorizontalHeaderLabels(map.values())

        for i, row in enumerate(self._data):
            for j, key in enumerate(map):
                item = QTableWidgetItem(row[key])

                t.setItem(i, j, item)


        t.resizeColumnsToContents()
