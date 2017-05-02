from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .a_WDBMolecule import WDBMolecule
import a99


__all__ = ["WMolConst"]


class WMolConst(a99.WBase):
    """
    Widget for the user to inform molecular parameters. Has a embedded WDBMolecule
    """

    # Emitted whenever the value of the molecule id changes
    # (actually propagates signal from the embedded WDBMolecule widget)
    id_changed = pyqtSignal()

    @property
    def fieldnames(self):
        return self._fieldnames

    @property
    def constants(self):
        """Returns a dictionary with all molecular constants"""
        ret = {}
        for fieldname in self._fieldnames:
            ret[fieldname] = self[fieldname]
        return ret

    @property
    def row(self):
        """Wraps WDBMolecule.row"""
        return self.w_mol.row

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        self.flag_populating = False  # activated when populating table

        # # Internal state

        #
        self._fieldnames = ["fe", "do", "am", "bm", "ua", "ub", "te", "cro", "s"]


        # dictionary {(field name): (edit object), }
        # (will be populated later below together with edit widgets creation)
        self._edit_map = {}


        # # GUI design

        l = QVBoxLayout(self)
        a99.set_margin(l, 1)

        # ## State widget
        a = self.w_mol = WDBMolecule(self.parent_form)
        l.addWidget(a)
        a.id_changed.connect(self._w_mol_id_changed)

        # ## Title label
        a = self.apa = self.keep_ref(QLabel("<h4>Values to be used in calculations</h4>"))
        l.addWidget(a)
        a.setToolTip("If you values below, this will affect the conversion calculation, but the information will not be written back to the database")

        # ## Molecular constants edit fields

        lg = QGridLayout()
        l.addLayout(lg)
        nr, nc, n = 3, 3, len(self._fieldnames)
        # TODO not working but maybe wont use this widget anymore
        ti = a99.get_table_info("moldb", "molecule")
        for j in range(nc):
            # ### One grid layout for each column of fields
            ii = range(j, n, nc)
            for i in range(len(ii)):
                fieldname = self._fieldnames[ii[i]]
                info = ti[fieldname]
                caption = info["caption"] or fieldname
                a = QLabel(caption)
                e = QLineEdit("")
                tooltip = info["tooltip"]
                if tooltip:
                    a.setToolTip(tooltip)
                    e.setToolTip(tooltip)
                self._edit_map[fieldname] = e
                lg.addWidget(a, i, j*2)
                lg.addWidget(e, i, j*2+1)
            # if len(ii) < nr:
            #     # Adds spacer to cause the effect of aligning fields to the top when the column is not
            #     # full of fields
            #     lv.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), i+1, 0, 1, 2)


    def __getitem__(self, fieldname):
        """Allows dict-like access of molecular constants of interest. Returns float value or None"""
        if fieldname in self._fieldnames:
            try:
                return float(self._edit_map[fieldname].text())
            except ValueError:
                return None


    def validate(self):
        """Returns True if all edit fields can be converted to float, otherwise False"""
        ret = True
        for fieldname in self._fieldnames:
            try:
                _ = float(self[fieldname])
            except ValueError:
                self.add_log_error("Failed converting field '{}' to float".format(fieldname))
                ret = False
                break
        return ret


    def None_to_zero(self):
        """Fills missing values with zeros"""
        for edit in self._edit_map.values():
            if len(edit.text().strip()) == 0:
                edit.setText("0")


    def _w_mol_id_changed(self):
        """Transfer values from self.data to edit fields below the table widget"""
        # id_ = print("State id changed to ", self.w_state.id)
        row = self.w_mol.row
        # if not row:
        #     return
        for fieldname, edit in self._edit_map.items():
            value = "" if not row else row[fieldname]
            edit.setText(str(value) if value is not None else "")

        self.id_changed.emit()
