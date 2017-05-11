from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from a99 import WDBRegistry
import a99
from .a_WDBFCF import *


__all__ = ["WDBSystem"]


# Field names to leave out of table widget
_FIELDNAMES_OUT = ("id_molecule",)


class WDBSystem(WDBRegistry):
    """Registry for table 'system'"""

    def __init__(self, *args):
        WDBRegistry.__init__(self, *args)
        self._id_molecule = None

    def set_id_molecule(self, id_):
        """Sets molecule id and re-populates table"""
        self._id_molecule = id_
        self._populate()

    def _populate(self, restore_mode=None):
        """
        Populates table widget

        Args:
            restore_mode: how to reposition cursor:
                - "index": tries to restore same row index
                - anything else: does not re-position
        """
        self._flag_populating = True
        try:
            curr_idx = self.tableWidget.currentRow()

            t = self.tableWidget
            rows = a99.cursor_to_rows(self._f.query_system(id_molecule=self._id_molecule))
            ti = self._f.get_table_info("system")
            fieldnames = [name for name in ti if name not in _FIELDNAMES_OUT]
            # unfortunately QTableWidget is not prepared to show HTML col_names = [row["caption"] or row["name"] for row in ti if not row["name"] in FIELDNAMES_OUT]
            col_names = fieldnames
            nr, nc = len(rows), len(fieldnames)

            a99.reset_table_widget(t, nr, nc)
            t.setHorizontalHeaderLabels(col_names)

            if nr > 0:
                for i, row in enumerate(rows):
                    for j, fieldname in enumerate(fieldnames):
                        cell = row[fieldname]
                        item = QTableWidgetItem("" if cell is None else str(cell))
                        t.setItem(i, j, item)
            t.resizeColumnsToContents()
            self._data = rows

            if restore_mode == "index":
                if -1 < curr_idx < t.rowCount():
                    t.setCurrentCell(curr_idx, 0)
        finally:
            self._flag_populating = False
            self._wanna_emit_id_changed()

    def _get_edit_params(self):
        """Returns a Parameters object containing information about the fields that may be edited"""
        ti = self._f.get_table_info("system")
        params = a99.table_info_to_parameters(ti)
        params = [p for p in params if not p.name.startswith("id")]
        return params

    def _get_edit_field_names(self):
        """Returns a list with the names of the fields that may be edited"""
        params = self._get_edit_params()
        ret = [p.name for p in params]
        return ret

    def _do_on_insert(self):
        params = self._get_edit_params()
        form = a99.XParametersEditor(specs=params, title="Insert Electronic System")
        r = form.exec_()
        if r == QDialog.Accepted:
            kwargs = form.get_kwargs()
            conn = self._f.get_conn()
            s = "insert into system (id_molecule, {}) values ({}, {})".\
                format(", ".join([p.name for p in params]),
                       self._id_molecule,
                       ", ".join(["?"]*len(params)))
            cursor = conn.execute(s, list(kwargs.values()))
            id_ = cursor.lastrowid
            conn.commit()
            self._populate(False)
            self._find_id(id_)
            return True

    def _do_on_edit(self):
        r, form = a99.show_edit_form(self.row, self._get_edit_field_names(), "Edit Electronic System")
        if r == QDialog.Accepted:
            kwargs = form.get_kwargs()
            id_ = self.row["id"]
            s = "update system set {} where id = {}".format(
                ", ".join(["{} = '{}'".format(a, b) for a, b in kwargs.items()]), id_)
            conn = self._f.get_conn()
            conn.execute(s)
            conn.commit()
            self._populate()
            self._find_id(id_)
            return True

    def _do_on_delete(self):
        r = QMessageBox.question(None, "Delete Electronic System",
                                 "Are you sure?",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r == QMessageBox.Yes:
            conn = self._f.get_conn()
            id_ = self.row["id"]
            conn.execute("delete from system where id = ?", [id_])
            conn.commit()

            self._populate("index")
            return True
