from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from a99 import WDBRegistry
import a99


__all__ = ["WDBRegistry"]

class WDBMolecule(WDBRegistry):
    """Registry for table 'molecule'"""


    def __init__(self, *args):
        WDBRegistry.__init__(self, *args)

    # # Override

    def _f_changed(self):
        self._populate()
#        self._move_to_first()

    def _find_formula(self, formula):
        """Moves to row where formula is (if found, otherwise does nothing)"""
        for i, row in enumerate(self._data):
            if row["formula"] == formula:
                self.tableWidget.setCurrentCell(i, 0)
                break

    def _populate(self, restore_mode=None):
        """
        Populates table widget

        Args:
            restore_mode: how to reposition cursor:
                "formula": tries to re-position at same formula as before
                "index": tries to restore same row index
                anything else: does not re-position
        """

        if self._f is None:
            return

        self._flag_populating = True
        try:
            t = self.tableWidget
            if self._f is None:
                a99.reset_table_widget(t, 0, 0)
                return

            curr_idx = self.tableWidget.currentRow()
            curr_row = self.row

            fieldnames = list(self._f.get_table_info("molecule"))
            rows = a99.cursor_to_rows(self._f.query_molecule())
            nr, nc = len(rows), len(fieldnames)
            a99.reset_table_widget(t, nr, nc)
            t.setHorizontalHeaderLabels(fieldnames)
            if nr > 0:
                for i, row in enumerate(rows):
                    for j, fieldname in enumerate(fieldnames):
                        cell = row[fieldname]
                        item = QTableWidgetItem("" if cell is None else str(cell))
                        t.setItem(i, j, item)
            t.resizeColumnsToContents()
            self._data = rows

            if restore_mode == "formula":
                if curr_row:
                    self._find_formula(curr_row["formula"])
            elif restore_mode == "index":
                if -1 < curr_idx < t.rowCount():
                    t.setCurrentCell(curr_idx, 0)
        finally:
            self._flag_populating = False
            self._wanna_emit_id_changed()


    def _get_edit_params(self):
        """Returns a Parameters object containing information about the fields that may be edited"""
        ti = self._f.get_table_info("molecule")
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
        form = a99.XParametersEditor(specs=params, title="Insert molecule")
        r = form.exec_()
        if r == QDialog.Accepted:
            kwargs = form.get_kwargs()
            conn = self._f.get_conn()
            s = "insert into molecule({}) values ({})".format(", ".join([p.name for p in params]),
                                                              ", ".join(["?"]*len(params)))
            cursor = conn.execute(s, list(kwargs.values()))
            id_ = cursor.lastrowid
            conn.commit()
            self._populate(False)
            self._find_id(id_)
            return True


    def _do_on_edit(self):
        r, form = a99.show_edit_form(self.row, self._get_edit_field_names(), "Edit molecule")
        if r == QDialog.Accepted:
            kwargs = form.get_kwargs()
            s = "update molecule set {} where id = {}".format(
                ", ".join(["{} = '{}'".format(a, b) for a, b in kwargs.items()]), self.row["id"])
            conn = self._f.get_conn()
            conn.execute(s)
            conn.commit()
            self._populate()
            self._find_formula(kwargs["formula"])
            return True


    def _do_on_delete(self):
        r = QMessageBox.question(None, "Delete molecule",
                                 "This will also delete all States, Systems, and PFANT molecules associated to this molecule!\n\nAre you sure?",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r == QMessageBox.Yes:
            conn = self._f.get_conn()
            id_ = self.row["id"]

            for row in conn.execute("select id from system where id_molecule = ?", [id_]):
                conn.execute("delete from fcf where id_system = ?", [row["id"]])
            conn.execute("delete from molecule where id = ?", [id_])
            conn.execute("delete from state where id_molecule = ?", [id_])
            conn.execute("delete from system where id_molecule = ?", [id_])
            conn.execute("delete from pfantmol where id_molecule = ?", [id_])
            conn.commit()

            self._populate("index")
            return True
