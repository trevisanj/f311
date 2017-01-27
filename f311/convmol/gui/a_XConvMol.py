from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
# from a_WState import WState
# import moldb as db
from .a_WStateConst import WStateConst
from .a_WMolConst import WMolConst
from .a_WFileMolDB import *
from ... import hapi
import os
import datetime
from collections import OrderedDict
import f311.filetypes as ft


__all__ = ["XConvMol"]


class _DataSource(a99.AttrsPart):
    """Represents a data source for molecular lines"""

    def __init__(self, name):
        a99.AttrsPart.__init__(self)
        self.name = name
        self.widget = None

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, self.name)



# This defines the order of the panels
_NAMES = ["HITRAN", "VALD3", "Kurucz", "TurboSpectrum", ]
_SOURCES = OrderedDict([[name, _DataSource(name)] for name in _NAMES])


class _WSource(a99.WBase):
    """Lists sources for molecular lines data"""


    @property
    def index(self):
        return self._get_index()

    @index.setter
    def index(self, x):
        self._buttons[x].setChecked(True)

    @property
    def source(self):
        """Returns _DataSource object or None"""
        i = self._get_index()
        if i < 0:
            return None
        return _SOURCES[_NAMES[i]]

    index_changed = pyqtSignal()

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        self._buttons = []
        self._last_index = -1

        lw = QVBoxLayout()
        self.setLayout(lw)

        for ds in _SOURCES.values():
            b = self.keep_ref(QRadioButton(ds.name))
            b.clicked.connect(self._button_clicked)
            self._buttons.append(b)
            lw.addWidget(b)

    def _button_clicked(self):
        i = self._get_index()
        if i != self._last_index:
            self._last_index = i
            self.index_changed.emit()


    def _get_index(self):
        for i, b in enumerate(self._buttons):
            assert isinstance(b, QRadioButton)
            if b.isChecked():
                return i
        return -1


class _WSelectSaveFile(a99.WBase):
    @property
    def value(self):
        return self._get_value()

    @value.setter
    def value(self, x):
        self.edit.setText(x)

    # # Emitted whenever the valu property changes **to a valid value**
    wants_auto = pyqtSignal()

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        self._last_value = None

        self._type = None
        self.dialog_title = "Save output as"
        self.dialog_path = "."
        self.dialog_wild = "*.*;;*.dat"

        lw = QHBoxLayout()
        self.setLayout(lw)

        t = self.label = self.keep_ref(QLabel("Save output as"))
        lw.addWidget(t)

        e = self.edit = QLineEdit()
        e.textChanged.connect(self.edit_changed)
        t.setBuddy(e)
        lw.addWidget(e)
        # e.setReadOnly(True)

        b = self.button_auto = QToolButton()
        lw.addWidget(b)
        b.clicked.connect(self.wants_auto)
        b.setIcon(a99.get_icon("leaf-plant"))
        b.setToolTip("Make up file name")
        b.setFixedWidth(30)

        b = self.button = QToolButton()
        lw.addWidget(b)
        b.clicked.connect(self.on_button_clicked)
        b.setIcon(a99.get_icon("document-save"))
        b.setToolTip("Choose file name to save as")
        b.setFixedWidth(30)

        # Forces paint red if invalid
        self.edit_changed()

    def on_button_clicked(self, _):
        self._on_button_clicked()

    def edit_changed(self):
        flag_valid = self.validate()
        a99.style_widget_valid(self.edit, not flag_valid)
        # if flag_valid:
        #     self._wanna_emit()

    def validate(self):
        """Returns True/False whether value is valid, i.e., existing file or directory"""
        value = self._get_value().strip()
        return len(value) > 0 and not os.path.isdir(value)

    def _on_button_clicked(self):
        path_ = self.edit.text().strip()
        if len(path_) == 0:
            path_ = self.dialog_path
        res = QFileDialog.getSaveFileName(self, self.dialog_title, path_, self.dialog_wild)[0]
        if res:
            res = res[0]
            self.edit.setText(res)
            self.dialog_path = res

    # def _wanna_emit(self):
    #     value_now = self._get_value()
    #     if value_now != self._last_value:
    #         self._last_value = value_now
    #         self.valueChanged.emit()

    def _get_value(self):
        return self.edit.text().strip()


class _WHitranPanel(a99.WBase):

    @property
    def data(self):
        """
        Returns value in hapi.LOCAL_TABLE_CACHE, or None. This variable is a dictionary

        See hapi.py for structure of this variable
        """
        idx = self.tableWidget.currentRow()
        if idx < 0:
            return None
        return hapi.LOCAL_TABLE_CACHE[self.tableWidget.item(idx, 0).text()]

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        self._flag_populating = False

        lw = QVBoxLayout()
        self.setLayout(lw)

        lw.addWidget(self.keep_ref(QLabel("HITRAN")))


        lg = QGridLayout()
        lw.addLayout(lg)

        a = self.keep_ref(QLabel("HITRAN 'data cache' directory"))
        w = self.w_dir = a99.WSelectDir(self.parent_form)
        a.setBuddy(w)
        w.valueChanged.connect(self.dir_changed)
        lg.addWidget(a, 0, 0)
        lg.addWidget(w, 0, 1)

        a = self.tableWidget = QTableWidget()
        lw.addWidget(a)
        a.setSelectionMode(QAbstractItemView.SingleSelection)
        a.setSelectionBehavior(QAbstractItemView.SelectRows)
        a.setEditTriggers(QTableWidget.NoEditTriggers)
        a.setFont(a99.MONO_FONT)
        a.setAlternatingRowColors(True)
        a.currentCellChanged.connect(self.on_tableWidget_currentCellChanged)

        # forces populate table with 'Python HITRAN API data cache' in local directory
        self.dir_changed()

    def on_tableWidget_currentCellChanged(self, curx, cury, prevx, prevy):
        pass

    def dir_changed(self):
        self._populate()


    def _populate(self):
        self._flag_populating = True
        try:
            # Changed HAPI working directory
            hapi.VARIABLES['BACKEND_DATABASE_NAME'] = self.w_dir.value
            # Loads all molecular lines data to memory
            hapi.loadCache()

            # Discounts "sampletab" table from HAPI cache, hence the "-1" below
            nr, nc = len(hapi.LOCAL_TABLE_CACHE)-1, 2
            t = self.tableWidget
            a99.reset_table_widget(t, nr, nc)
            t.setHorizontalHeaderLabels(["Table filename (.data & .header)", "Number of spectral lines"])

            i = 0
            for h, (name, data) in enumerate(hapi.LOCAL_TABLE_CACHE.items()):
                if name == "sampletab":
                    continue

                header = data["header"]

                item = QTableWidgetItem(name)
                t.setItem(i, 0, item)

                item = QTableWidgetItem(str(header["number_of_rows"]))
                t.setItem(i, 1, item)

                i += 1

            t.resizeColumnsToContents()

            # self._data = rows
            #
            # if restore_mode == "formula":
            #     if curr_row:
            #         self._find_formula(curr_row["formula"])
            # elif restore_mode == "index":
            #     if -1 < curr_idx < t.rowCount():
            #         t.setCurrentCell(curr_idx, 0)
        finally:
            self._flag_populating = False
            # self._wanna_emit_id_changed()


class _WVald3Panel(a99.WBase):
    """
    This panel allows to load a Vald3 file and browse through its species (molecules only)

    The goal is to choose one molecule
    """

    @property
    def data(self):
        """
        Returns FileVald3 with a single species"""

        idx = self.tableWidget.currentRow()
        if idx < 0:
            return None

        f = ft.FileVald3()
        f.speciess = [self._f.speciess[idx]]
        return f

    @property
    def is_molecule(self):
        data = self.data
        return data is not None and data.speciess[0].formula not in a99.symbols

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        self._flag_populating = False
        self._f = None  # FileVald3

        lw = QVBoxLayout()
        self.setLayout(lw)

        lw.addWidget(self.keep_ref(QLabel("VALD3")))

        lg = QGridLayout()
        lw.addLayout(lg)

        a = self.keep_ref(QLabel("VALD3 extended-format file"))
        w = self.w_file = a99.WSelectFile(self.parent_form)
        a.setBuddy(w)
        w.valueChanged.connect(self.file_changed)
        lw.addWidget(w)
        lg.addWidget(a, 0, 0)
        lg.addWidget(w, 0, 1)


        a = self.tableWidget = QTableWidget()
        lw.addWidget(a)
        a.setSelectionMode(QAbstractItemView.SingleSelection)
        a.setSelectionBehavior(QAbstractItemView.SelectRows)
        a.setEditTriggers(QTableWidget.NoEditTriggers)
        a.setFont(a99.MONO_FONT)
        a.setAlternatingRowColors(True)
        a.currentCellChanged.connect(self.on_tableWidget_currentCellChanged)

        l = self.label_warning = QLabel()
        l.setStyleSheet("QLabel {{color: {}}}".format(a99.COLOR_WARNING))
        lw.addWidget(l)

        # forces populate table with 'Python HITRAN API data cache' in local directory
        # self.file_changed()

    def on_tableWidget_currentCellChanged(self, curx, cury, prevx, prevy):
        self.label_warning.setText("Need a molecule, not atom"
                                   if self.data is not None and not self.is_molecule else "")

    def file_changed(self):
        self._populate()


    def _populate(self):
        self._flag_populating = True
        try:
            f = self._f = ft.FileVald3()
            f.load(self.w_file.value)

            nr, nc = len(f), 3
            t = self.tableWidget
            a99.reset_table_widget(t, nr, nc)
            t.setHorizontalHeaderLabels(["VALD3 species", "Number of spectral lines", "Atom/Molecule"])

            for i, species in enumerate(f):
                item = QTableWidgetItem(str(species))
                t.setItem(i, 0, item)
                item = QTableWidgetItem(str(len(species)))
                t.setItem(i, 1, item)
                item = QTableWidgetItem("Atom" if species.formula in a99.symbols else "Molecule")
                t.setItem(i, 2, item)

            t.resizeColumnsToContents()

        except Exception as e:
            self._f = None
            self.add_log_error("Error reading contents of file '{}': '{}'".format(self.w_file.value, a99.str_exc(e)), True)
            raise

        finally:
            self._flag_populating = False
            # self._wanna_emit_id_changed()

class _WKuruczPanel(a99.WBase):
    """
    This panel allows to load a Kurucz molecular lines file
    """

    @property
    def data(self):
        """Returns FileKuruczMolecule or None"""
        return self._f

    @property
    def flag_hlf(self):
        return self.checkbox_hlf.isChecked()

    @property
    def flag_normhlf(self):
        return self.checkbox_normhlf.isChecked()

    @property
    def flag_fcf(self):
        return self.checkbox_fcf.isChecked()

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        self._f = None  # FileKuruczMolecule

        lw = QVBoxLayout()
        self.setLayout(lw)

        lw.addWidget(self.keep_ref(QLabel("Kurucz")))

        lg = QGridLayout()
        lw.addLayout(lg)

        a = self.keep_ref(QLabel("Kurucz molecular lines file"))
        w = self.w_file = a99.WSelectFile(self.parent_form)
        w.valueChanged.connect(self.file_changed)
        lg.addWidget(a, 0, 0)
        lg.addWidget(w, 0, 1)

        a = self.keep_ref(QLabel("Calculate 'gf' based on Hönl-London factors (HLFs)"))
        w = self.checkbox_hlf = QCheckBox()
        w.setToolTip("If selected, will ignore 'loggf' from Kurucz file and\n"
                     "calculate 'gf' using Hönl-London factors formulas taken from Kovacz (1969)")
        lg.addWidget(a, 1, 0)
        lg.addWidget(w, 1, 1)

        a = self.keep_ref(QLabel("Apply normalization factor for HLFs to add up to 1 (for fixed J)"))
        w = self.checkbox_normhlf = QCheckBox()
        w.setToolTip("If selected, calculated 'gf's will be divided by\n"
                     "2 / ((2 * J2l + 1) * (2 * S + 1)*(2 - DELTAK))")
        lg.addWidget(a, 2, 0)
        lg.addWidget(w, 2, 1)

        a = self.keep_ref(QLabel("Multiply calculated 'gf' by Franck-Condon factor"))
        w = self.checkbox_fcf = QCheckBox()
        w.setToolTip("If selected, incorporates internally calculated Franck-Condon factor"
                     "into the calculated 'gf'")
        lg.addWidget(a, 3, 0)
        lg.addWidget(w, 3, 1)


        lw.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def file_changed(self):
        try:
            f = self._f = ft.FileKuruczMolecule()
            f.load(self.w_file.value)
        except Exception as e:
            self._f = None
            self.add_log_error("Error reading contents of file '{}': '{}'".format(self.w_file.value, a99.str_exc(e)), True)
            raise


class _WTurboSpectrumPanel(a99.WBase):
    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        lw = QVBoxLayout()
        self.setLayout(lw)

        lw.addWidget(self.keep_ref(QLabel("TurboSpectrum")))



class XConvMol(a99.XFileMainWindow):
    def __init__(self, parent=None, fileobj=None):
        a99.XFileMainWindow.__init__(self, parent)

        # # Synchronized sequences
        _VVV = ft.FileMolDB.description
        self.tab_texts =  ["{} (Alt+&1)".format(_VVV), "Conversion (Alt+&2)", "Log (Alt+&3)"]
        self.flags_changed = [False, False]
        self.save_as_texts = ["Save %s as..." % _VVV, None, None]
        self.open_texts = ["Load %s" % _VVV, None, None]
        self.clss = [ft.FileMolDB, None, None]  # save class
        self.clsss = [(ft.FileMolDB,), None, None]  # accepted load classes
        self.wilds = ["*.sqlite", None, None]  # e.g. '*.fits'
        self.editors = [a99.NullEditor(), a99.NullEditor(), a99.NullEditor()]  # editor widgets, must comply ...
        tw0 = self.tabWidget
        tw0.setTabText(1, self.tab_texts[2])


        lv = self.keep_ref(QVBoxLayout(self.gotting))
        me = self.moldb_editor = WFileMolDB(self)
        lv.addWidget(me)
        me.edited.connect(self._on_edited)
        self.editors[0] = me


        # # Second tab: files

        w = self.keep_ref(QWidget())
        tw0.insertTab(1, w, self.tab_texts[1])


        # ## Vertical layout: source and destination stacked
        lsd = self.keep_ref(QVBoxLayout(w))

        # ### Horizontal layout: sources radio buttons, source-specific setup area

        lh = self.keep_ref(QHBoxLayout())
        lsd.addLayout(lh)

        # #### Vertical layout: source radio group box

        lss = QVBoxLayout()
        lh.addLayout(lss)

        # ##### Source radio buttons
        lss.addWidget(self.keep_ref(QLabel("<b>Source</b>")))
        w = self.w_source = _WSource(self)
        w.index_changed.connect(self.source_changed)
        lss.addWidget(w)
        lss.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))


        # #### Adds configuration panels for various sources
        # Only one panel should be visible at a time
        # **Note** The order here doesn't matter
        panels = {}
        panels["HITRAN"] = self.w_hitran = _WHitranPanel(self)
        panels["VALD3"] = self.w_vald3 = _WVald3Panel(self)
        panels["TurboSpectrum"] = self.w_turbo = _WTurboSpectrumPanel(self)
        panels["Kurucz"] = self.w_kurucz = _WKuruczPanel(self)
        for name in _NAMES:
            p = panels[name]
            ds = _SOURCES[name]
            ds.widget = p
            lh.addWidget(p)

        # ### Output file specification

        w0 = self.w_out = _WSelectSaveFile(self)
        w0.wants_auto.connect(self.wants_auto)
        lsd.addWidget(w0)

        # ### "Convert" button

        lmn = QHBoxLayout()
        lsd.addLayout(lmn)
        lmn.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        b = self.button_convert = QPushButton("&Run Conversion")
        b.clicked.connect(self.convert_clicked)
        lmn.addWidget(b)
        b = self.button_convert = QPushButton("&Open file")
        b.clicked.connect(self.open_mol_clicked)
        lmn.addWidget(b)


        # # # Log facilities
        #
        # sb = self.statusBar()
        # l = self.label_last_log = QLabel()
        # sb.addWidget(l)
        #
        # w = self.textEdit_log = QTextEdit()
        # w.setReadOnly(True)
        # tw0.addTab(w, "Log messages (Alt+&L)")
        #
        # # Final adjustments

        tw0.setCurrentIndex(0)
        # Forces only one of the source panels to visible
        self.w_source.index = 0
        self.source_changed()
        self.setWindowTitle("(to) PFANT Molecular Lines Converter")

        a99.nerdify(self)

        if fileobj is not None:
            self.load(fileobj)

        self.installEventFilter(self)

    def eventFilter(self, obj_focused, event):
        if event.type() == QEvent.KeyPress:
            # To help my debugging
            if event.key() == Qt.Key_F12:
                self.moldb_editor.w_mol.tableWidget.setCurrentCell(6, 0)
                self.moldb_editor.w_state.tableWidget.setCurrentCell(5, 0)
                self.w_source._buttons[2].setChecked(True)
                self.source_changed()
                self.w_kurucz.w_file.edit.setText("ohaxupdate.asc")
                self.tabWidget.setCurrentIndex(1)
        return False

    def wants_auto(self):
        name = _NAMES[self.w_source.index]
        filename = None
        if name == "HITRAN":
            lines = self.w_hitran.data
            if lines:
                filename = "{}.dat".format(lines["header"]["table_name"])

        if filename is None:
            # Default
            filename = a99.new_filename("mol", "dat")
        self.w_out.value = filename


    # def on_fill_missing(self):
    #     self.w_mol.None_to_zero()
    #     self.w_state.None_to_zero()

    def source_changed(self):
        idx = self.w_source.index
        for i, ds in enumerate(_SOURCES.values()):
            ds.widget.setVisible(i == idx)
            # print("Widget", ds.widget, "is visible?", ds.widget.isVisible())

    # def mol_id_changed(self):
    #     id_ = self.w_mol.w_mol.id
    #     row = self.w_mol.w_mol.row
    #     self.w_state.set_id_molecule(id_)
    #     s = "States (no molecule selected)" if not row else "Select a State for molecule '{}'".format(row["formula"])
    #     self.title_state.setText(a99.format_title0(s))

    def convert_clicked(self):
        cm = pf.convmol
        try:
            errors = []
            name = self.w_source.source.name
            w_mol = self.moldb_editor.w_mol
            w_state = self.moldb_editor.w_state
            mol_row = w_mol.row
            mol_consts = mol_row
            state_consts = w_state.row
            filename = self.w_out.value
            if not mol_row:
                errors.append("Molecule not selected")
            elif any([x is None for x in mol_consts.values()]):
                errors.append("There are empty molecule-wide constants")
            if not state_consts:
                errors.append("State not selected")
            elif any([x is None for x in state_consts.values()]):
                errors.append("There are empty state-wide constants")
            if not self.w_out.validate():
                errors.append("Output filename is invalid")

            lines, sols_calculator = None, None
            if len(errors) == 0:
                # Source-dependant calculation of "sets of lines"
                if name == "HITRAN":
                    lines = self.w_hitran.data

                    if lines is None:
                        errors.append("HITRAN table not selected")
                    else:
                        sols_calculator = cm.hitran_to_sols
                elif name == "VALD3":
                    if not self.w_vald3.is_molecule:
                        errors.append("Need a VALD3 molecule")
                    else:
                        lines = self.w_vald3.data
                        sols_calculator = cm.vald3_to_sols
                elif name == "Kurucz":
                    lines = self.w_kurucz.data

                    sols_calculator = lambda *args: cm.kurucz_to_sols(*args,
                        flag_hlf=self.w_kurucz.flag_hlf, flag_normhlf=self.w_kurucz.flag_normhlf,
                        flag_fcf=self.w_kurucz.flag_fcf)
                else:
                    a99.show_message("{}-to-PFANT conversion not implemented yet, sorry".
                                    format(name))
                    return

            if len(errors) == 0:
                # Finally the conversion to PFANT molecular lines file

                # TODO **MAYBE NOT TIO-LIKE***
                mol_row.update(mol_consts)  # replaces possibly changed values for "fe", "do" etc.
                f, log = cm.make_file_molecules(mol_row, state_consts, lines,
                                                cm.calc_qgbd_tio_like, sols_calculator)
                ne = len(log.errors)
                if ne > 0:
                    self.add_log("Error messages:")
                    self.add_log("\n".join(log.errors))
                    self.add_log("{} error message{}".format(ne, "" if ne == 1 else "s"))

                if log.flag_ok:
                    f.save_as(filename)
                    self.add_log(
                        "Lines converted: {}/{}".format(f.num_lines, log.num_lines_in))

                    self.add_log("File '{}' generated successfully".format(filename))
                else:
                    self.add_log_error("Conversion was not possible")

            else:
                self.add_log_error("Cannot convert:\n  - " + ("\n  - ".join(errors)), True)

        except Exception as e:
            a99.get_python_logger().exception("Conversion failed")
            self.add_log_error("Conversion failed: {}".format(a99.str_exc(e)), True)


    def open_mol_clicked(self):
        filename = self.w_out.value
        if len(filename) > 0:
            f = ft.FileMolecules()
            f.load(filename)
            vis = pf.VisMolecules()
            vis.use(f)