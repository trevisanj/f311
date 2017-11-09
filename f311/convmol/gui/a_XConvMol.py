from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
# from a_WState import WState
# import moldb as db
from ...explorer.gui.gui_convmol.a_WMolecularConstants import *
from ... import hapi
import os
import datetime
from collections import OrderedDict
import f311.filetypes as ft
import f311.pyfant as pf
import f311.explorer as ex
from f311.explorer.gui.gui_convmol.a_WFileMolConsts import *
from f311.explorer.gui.gui_convmol.a_WFileMolDB import *

__all__ = ["XConvMol"]


# Spacing for grid layouts
_LAYSP_GRID = 4
# Margin for grid layouts
_LAYMN_GRID = 0
# Spacing for vertical layouts
_LAYSP_V = 10
# Margin for vertical layouts ((caption, combobox); grid)
_LAYMN_V = 6


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
    def sourcename(self):
        source = self._get_source()
        if source is None:
            return None
        return source.name

    @sourcename.setter
    def sourcename(self, value):
        index = -1
        if value is not None:
            index = _NAMES.index(value)
        for i, b in enumerate(self._buttons):
            b.setChecked(i == index)
        self._check_index_changed(False)

    @property
    def source(self):
        return self._get_source()


    # Emitted if index changed by user, not programatically
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


    def _get_source(self):
        """Returns _DataSource object or None"""
        i = self._get_index()
        if i < 0:
            return None
        return _SOURCES[_NAMES[i]]

    def _button_clicked(self):
        self._check_index_changed()

    def _check_index_changed(self, flag_emit=True):
        i = self._get_index()
        if i != self._last_index:
            self._last_index = i
            if flag_emit:
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
        if x is None:
            x = ""
        self.edit.setText(x)

    @property
    def flag_valid(self):
        return self._flag_valid

    @flag_valid.setter
    def flag_valid(self, value):
        self._flag_valid = value
        self._update_gui()

    # Emitted whenever the valu property changes **to a valid value**
    wants_autofilename = pyqtSignal()
    # Emitted whenever text changes
    changed = pyqtSignal()

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        self._last_value = None
        self._flag_valid = None

        self._type = None
        self.dialog_title = "Save output as"
        self.dialog_path = "."
        self.dialog_wild = "*.*;;*.dat"

        lw = QHBoxLayout()
        self.setLayout(lw)

        t = self.label = self.keep_ref(QLabel("Save output as"))
        lw.addWidget(t)

        e = self.edit = QLineEdit()
        e.textEdited.connect(self.edit_changed)
        t.setBuddy(e)
        lw.addWidget(e)
        # e.setReadOnly(True)

        b = self.button_autofilename = QToolButton()
        lw.addWidget(b)
        b.clicked.connect(self.wants_autofilename)
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
        self._update_gui()

    def on_button_clicked(self, _):
        self._on_button_clicked()

    def edit_changed(self):
        self.changed.emit()

    def _update_gui(self):
        a99.style_widget_valid(self.edit, self._flag_valid)

    def _on_button_clicked(self):
        path_ = self.edit.text().strip()
        if len(path_) == 0:
            path_ = self.dialog_path
        res = QFileDialog.getSaveFileName(self, self.dialog_title, path_, self.dialog_wild)[0]
        if res:
            # res = res[0]
            self.edit.setText(res)
            self.changed.emit()
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

    def __init__(self, parent):
        a99.WBase.__init__(self, parent.parent_form)

        self.w_conv = parent

        self._flag_populating = False

        lw = QVBoxLayout()
        self.setLayout(lw)

        lw.addWidget(self.keep_ref(QLabel("HITRAN")))


        lg = QGridLayout()
        lw.addLayout(lg)

        a = self.keep_ref(QLabel("HITRAN 'data cache' directory"))
        w = self.w_dir = a99.WSelectDir(self.parent_form)
        a.setBuddy(w)
        w.changed.connect(self.dir_changed)
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


# TODO other panels must comply with Kurucz
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

    def __init__(self, parent):
        a99.WBase.__init__(self, parent.parent_form)

        self.w_conv = parent

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
        w.changed.connect(self.file_changed)
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

        else:
            self.clear_log()

        finally:
            self._flag_populating = False
            # self._wanna_emit_id_changed()


class _WKuruczPanel(a99.WBase):
    """
    This panel allows to load a Kurucz molecular lines file
    """

    @property
    def data(self):
        """Returns FileKuruczMoleculeBase or None"""
        return self._flines

    @property
    def iso(self):
        return self._get_iso()

    @iso.setter
    def iso(self, value):
        self._set_iso(value)

    def __init__(self, parent):
        a99.WBase.__init__(self, parent.parent_form)

        self.w_conv = parent

        self._flines = None  # FileKuruczMoleculeBase
        # list of integers, filled when file is loaded
        self._isotopes = []

        lw = QVBoxLayout()
        self.setLayout(lw)

        lw.addWidget(self.keep_ref(QLabel("Kurucz")))

        lg = QGridLayout()
        lw.addLayout(lg)

        i_row = 0
        a = self.keep_ref(QLabel("Kurucz molecular lines file"))
        w = self.w_file = a99.WSelectFile(self.parent_form)
        w.changed.connect(self._file_changed)
        lg.addWidget(a, i_row, 0)
        lg.addWidget(w, i_row, 1)
        i_row += 1

        a = self.keep_ref(QLabel("Isotope"))
        w = self.combobox_isotope = QComboBox()
        w.currentIndexChanged.connect(self.changed)
        lg.addWidget(a, i_row, 0)
        lg.addWidget(w, i_row, 1)
        i_row += 1

        lw.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _set_iso(self, value):
        if value is None:
            idx = 0
        else:
            try:
                idx = self._isotopes.index(value)+1
            except ValueError:
                idx = 0
        cb = self.combobox_isotope
        if cb.count() > 0:
            save = cb.blockSignals(True)
            cb.setCurrentIndex(idx)
            cb.blockSignals(save)

    def _get_iso(self):
        idx = self.combobox_isotope.currentIndex()
        if idx <= 0:
            return None
        return self._isotopes[idx - 1]

    def _file_changed(self):

        f = None
        try:
            f = self._load_lines()

        except Exception as e:
            self._flines = None
            self._isotopes = []
            msg = "Error reading contents of file '{}': '{}'".format(self.w_file.value,
                                                                              a99.str_exc(e))
            self.add_log_error(msg, True)
            a99.get_python_logger().exception(msg)

        # Tries to restore iso without much compromise
        self._set_iso(self.w_conv.f.obj["iso"])
        self.w_conv.f.obj["iso"] = self._get_iso()

        self.w_file.flag_valid = f is not None
        self.changed.emit()

    def _load_lines(self):
        filename = self.w_file.value
        f = self._flines = ft.load_kurucz_mol(filename) if os.path.isfile(filename) else None
        self.w_file.flag_valid = f is not None
        self._update_gui_iso()
        return f

    def _update_gui_iso(self):
        """Updates Isotope combobox"""
        f = self._flines
        cb = self.combobox_isotope
        save = cb.blockSignals(True)
        try:
            cb.clear()
            if f is not None:
                if f.__class__ != ft.FileKuruczMolecule:
                    cb.addItem("(all (file is old-format))")
                else:
                    self._isotopes = list(set([line.iso for line in f]))
                    self._isotopes.sort()
                    cb.addItem("(all)")
                    cb.addItems([str(x) for x in self._isotopes])
        finally:
            cb.blockSignals(save)


class _WTurboSpectrumPanel(a99.WBase):
    def __init__(self, parent):
        a99.WBase.__init__(self, parent.parent_form)

        self.w_conv = parent

        lw = QVBoxLayout()
        self.setLayout(lw)

        lw.addWidget(self.keep_ref(QLabel("TurboSpectrum")))


class _WConv(a99.WConfigEditor):

    convert_clicked = pyqtSignal()
    open_mol_clicked = pyqtSignal()

    @property
    def flag_hlf(self):
        return self.checkbox_hlf.isChecked()

    @flag_hlf.setter
    def flag_hlf(self, value):
        a99.set_checkbox_value(self.checkbox_hlf, value)

    @property
    def flag_normhlf(self):
        return self.checkbox_normhlf.isChecked()

    @flag_normhlf.setter
    def flag_normhlf(self, value):
        a99.set_checkbox_value(self.checkbox_normhlf, value)

    @property
    def flag_fcf(self):
        return self.checkbox_fcf.isChecked()

    @flag_fcf.setter
    def flag_fcf(self, value):
        a99.set_checkbox_value(self.checkbox_fcf, value)

    @property
    def flag_special_fcf(self):
        return self.checkbox_special_fcf.isChecked()

    @flag_special_fcf.setter
    def flag_special_fcf(self, value):
        a99.set_checkbox_value(self.checkbox_special_fcf, value)

    @property
    def flag_spinl(self):
        return self.checkbox_spinl.isChecked()

    @flag_spinl.setter
    def flag_spinl(self, value):
        a99.set_checkbox_value(self.checkbox_spinl, value)

    @property
    def flag_quiet(self):
        return self.checkbox_quiet.isChecked()

    @flag_quiet.setter
    def flag_quiet(self, value):
        a99.set_checkbox_value(self.checkbox_quiet, value)


    def __init__(self, parent_form):
        a99.WConfigEditor.__init__(self, parent_form)

        self.w_molconsts = parent_form.w_molconsts

        # ## Vertical layout: source and destination stacked
        lsd = self.layout_editor

        # ### Horizontal layout: sources radio buttons, source-specific setup area

        lh = self.keep_ref(QHBoxLayout())
        # a99.set_margin
        lsd.addLayout(lh)

        # #### Vertical layout: source radio group box

        lss = QVBoxLayout()
        lh.addLayout(lss)

        # ##### Source radio buttons
        lss.addWidget(self.keep_ref(QLabel("<b>Source</b>")))
        w = self.w_source = _WSource(self.parent_form)
        w.index_changed.connect(self._source_changed)
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
            ds = _SOURCES[name]
            ds.widget = p = panels[name]
            lh.addWidget(p)
            p.changed.connect(self._panel_changed)

        # ### Flags panel

        fr = self.frame_flags = a99.get_frame()
        lsd.addWidget(fr)
        lfr = self.layout_flags = QVBoxLayout(fr)
        lfr.setSpacing(_LAYSP_V)
        a99.set_margin(lfr, _LAYMN_V)

        la = self.label_flags = QLabel("<b>Flags</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        lfr.addWidget(la)

        lg = QGridLayout()
        lg.setSpacing(_LAYSP_GRID)
        a99.set_margin(lg, _LAYMN_GRID)
        lfr.addLayout(lg)

        i_row = 0

        a = self.keep_ref(QLabel("Calculate 'gf' based on\n"
                                 "Hönl-London factors (HLFs)"))
        w = self.checkbox_hlf = QCheckBox()
        w.stateChanged.connect(self.changed)
        w.setToolTip("If selected, will ignore 'loggf' from Kurucz file and\n"
                     "calculate 'gf' using Hönl-London factors formulas taken from Kovacz (1969)")
        lg.addWidget(a, i_row, 0)
        lg.addWidget(w, i_row, 1)
        i_row += 1

        a = self.keep_ref(QLabel("Apply normalization factor\n"
                                 "for HLFs to add up to 1 (for fixed J)"))
        w = self.checkbox_normhlf = QCheckBox()
        w.stateChanged.connect(self.changed)
        w.setToolTip("If selected, calculated 'gf's will be multiplied by\n"
                     "2 / ((2 * J2l + 1) * (2 * S + 1)*(2 - DELTAK))")
        lg.addWidget(a, i_row, 0)
        lg.addWidget(w, i_row, 1)
        i_row += 1

        a = self.keep_ref(QLabel("Multiply calculated 'gf' by\n"
                                 "Franck-Condon factor"))
        w = self.checkbox_fcf = QCheckBox()
        w.stateChanged.connect(self.changed)
        w.setToolTip("If selected, incorporates internally calculated Franck-Condon factor"
                     "into the calculated 'gf'")
        lg.addWidget(a, i_row, 0)
        lg.addWidget(w, i_row, 1)
        i_row += 1

        a = self.keep_ref(QLabel("Force 0.1 <= FCF < 1"))
        w = self.checkbox_special_fcf = QCheckBox()
        w.stateChanged.connect(self.changed)
        w.setToolTip("(*temporary*) If selected, makes 'fcf = fcf * 10 ** -(math.floor(math.log10(fcf)) + 1)'")
        lg.addWidget(a, i_row, 0)
        lg.addWidget(w, i_row, 1)
        i_row += 1

        a = self.keep_ref(QLabel("Use spin' for branch determination\n"
                                 "(spin'' is always used)"))
        w = self.checkbox_spinl = QCheckBox()
        w.stateChanged.connect(self.changed)
        w.setToolTip("If you tick this box, branches P12, P21, Q12, Q21, R21, R12 (i.e., with two numbers) become possible")
        lg.addWidget(a, i_row, 0)
        lg.addWidget(w, i_row, 1)
        i_row += 1

        a = self.keep_ref(QLabel("Quiet conversion"))
        w = self.checkbox_quiet = QCheckBox()
        w.setChecked(True)
        w.stateChanged.connect(self.changed)
        w.setToolTip("If selected, will show less error messages")
        lg.addWidget(a, i_row, 0)
        lg.addWidget(w, i_row, 1)
        i_row += 1








        # ### Output file specification

        w0 = self.w_out = _WSelectSaveFile(self.parent_form)
        w0.wants_autofilename.connect(self._wants_autofilename)
        w0.changed.connect(self._fn_output_changed)
        lsd.addWidget(w0)

        # ### "Convert" button

        lmn = QHBoxLayout()
        lsd.addLayout(lmn)
        lmn.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        b = self.button_convert = QPushButton("&Run Conversion")
        b.clicked.connect(self._convert_clicked)
        lmn.addWidget(b)
        b = self.button_convert = QPushButton("&Open result in mled.py")
        b.clicked.connect(self._open_mol_clicked)
        lmn.addWidget(b)


        # name, property
        self._map = [
            a99.CEMapItem("sourcename", self.w_source),
            a99.CEMapItem("fn_output", self.w_out, propertyname="value"),
            a99.CEMapItem("kurucz_iso", self.w_kurucz, propertyname="iso"),
            a99.CEMapItem("kurucz_fn_input", self.w_kurucz.w_file, propertyname="value"),
            a99.CEMapItem("flag_hlf", self),
            a99.CEMapItem("flag_normhlf", self),
            a99.CEMapItem("flag_fcf", self),
            a99.CEMapItem("flag_special_fcf", self),
            a99.CEMapItem("flag_spinl", self),
            a99.CEMapItem("flag_quiet", self),
        ]


    def _do_load(self, fobj):
        a99.WConfigEditor._do_load(self, fobj)
        self.w_kurucz._load_lines()
        # Redundant, but simplest way. After loading data, comboboxes will be positioned
        self._update_gui()

    def _update_gui(self):
        a99.WConfigEditor._update_gui(self)

        idx = self.w_source.index
        for i, ds in enumerate(_SOURCES.values()):
            ds.widget.setVisible(i == idx)

        self._update_w_out_flag_valid()
        # self._source_changed()

    def _update_w_out_flag_valid(self):
        self.w_out.flag_valid = self.w_out.value is not None and len(self.w_out.value) > 0

    def _panel_changed(self):
        """Called when anything in any panel changes"""
        self._update_fobj()
        self.changed.emit()

    def _fn_output_changed(self):
        """Called when anything in any panel changes"""
        self._update_fobj()
        self.changed.emit()
        self._update_w_out_flag_valid()

    def _source_changed(self):
        # if self._flag_updating_gui:
        #     return

            # print("Widget", ds.widget, "is visible?", ds.widget.isVisible())
        self._update_fobj()
        self._update_gui()
        self.changed.emit()

    def _wants_autofilename(self):
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
        self._update_fobj()
        self.changed.emit()

    def _convert_clicked(self):
        self.add_log("===BEGIN===")
        try:
            errors = self._validate()

            if len(errors) == 0:
                conv, errors = self._get_conv(errors)

            if len(errors) == 0:
                lines = self._get_lines()
                if lines is None:
                    errors.append("Molecular lines not specified")

            if len(errors) == 0:
                fobj, log = conv.make_file_molecules(lines)

                self._report_conversion(fobj, log)

                if log.flag_ok:
                    fobj.save_as(self.w_out.value)
                    self.add_log("File '{}' generated successfully".format(self.w_out.value))

            else:
                self.add_log_error("Cannot convert:\n  - " + ("\n  - ".join(errors)), True)

        except Exception as e:
            a99.get_python_logger().exception("Conversion failed")
            self.add_log_error("Conversion failed: {}".format(a99.str_exc(e)), True)

        self.add_log("===END===")

    def _report_conversion(self, fobj, log):
        ne = len(log.errors)
        if ne > 0:
            self.add_log("Error messages:")
            self.add_log("\n".join(log.errors))
            self.add_log("{} error message{}".format(ne, "" if ne == 1 else "s"))
        if log.flag_ok:
            if log.num_lines_skipped > 0:
                self.add_log(
                    "Lines filtered out: {}".format(log.num_lines_skipped))
                self.add_log("    Reasons:")
                kv = list(log.skip_reasons.items())
                kv.sort(key=lambda x: x[0])
                for key, value in kv:
                    self.add_log("      - {}: {}".format(key, value))
            ne = log.num_lines - log.num_lines_skipped - fobj.num_lines
            if ne > 0:
                self.add_log(
                    "Lines not converted because of error: {}".format(ne))
            self.add_log(
                "Lines converted: {}/{}".format(fobj.num_lines, log.num_lines))
        else:
            self.add_log_error("Conversion was not possible")

    def _get_conv(self, errors):
        import f311.convmol as cm

        name = self.w_source.source.name

        # (Data source name, Conv class)
        map = dict([("HITRAN", None),
               ("VALD3", None),
               ("Kurucz", cm.ConvKurucz)])

        cls = None
        conv = None
        try:
            cls = map[name]
        except KeyError:
            pass

        if cls is None:
            errors.append("{}-to-PFANT conversion not implemented yet, sorry".format(name))
        else:
            w = self.w_source.source.widget
            conv = cls(flag_hlf=self.flag_hlf,
                       flag_normhlf=self.flag_normhlf,
                       flag_fcf=self.flag_fcf,
                       flag_special_fcf=self.flag_special_fcf,
                       flag_quiet=self.flag_quiet,
                       flag_spinl=self.flag_spinl,
                       iso=w.iso)
            conv.fcfs = self.w_molconsts.fcfs
            conv.molconsts = self.w_molconsts.f.molconsts

        return conv, errors

    def _get_lines(self):
        """Creates a Conv object and """

        import f311.convmol as cm

        widget_panel = self.w_source.source.widget

        return widget_panel.data

    def _validate(self, ):
        """Validation of GUI. Returns errors"""
        errors = []

        molconsts = self.w_molconsts.f.molconsts

        molconsts_fieldnames_ignore = ["id_molecule", "id_pfantmol", "id_system", "id_statel",
                                       "id_state2l", "pfant_notes", "pfant_name"]
        if molconsts["id_molecule"] is None:
            errors.append("Molecule not selected")

        elif any([value is None for name, value in molconsts.items()
                  if name not in molconsts_fieldnames_ignore]):
            s_none = ", ".join(["'{}'".format(name) for name, value in molconsts.items()
                                if value is None and name not in molconsts_fieldnames_ignore])
            errors.append("There are empty molecular constants: {}".format(s_none))
        if not self.w_out.flag_valid:
            errors.append("Output filename is invalid")



        # Data-source-specific validation

        name = self.w_source.source.name

        if self.flag_fcf and self.w_molconsts.fcfs is None:
            errors.append(
                "Cannot multiply gf's by Franck-Condon Factors, as these are not available in molecular configuration")

        if name == "VALD3":
            if not self.w_vald3.is_molecule:
                errors.append("Need a VALD3 molecule")
        elif name == "Kurucz":
            pass


        return errors

    def _open_mol_clicked(self):
        filename = self.w_out.value
        if len(filename) > 0:
            f = ft.FileMolecules()
            f.load(filename)
            vis = ex.VisMolecules()
            vis.use(f)

    def _set_checkbox_value(self, w, value):
        save = w.blockSignals(True)
        try:
            w.setChecked(bool(value))
        finally:
            w.blockSignals(save)


class XConvMol(ex.XFileMainWindow):
    def _add_stuff(self):
        # Qt stuff tab #0: FileMolDB editor
        e0 = self.w_moldb = WFileMolDB(self)
        e0.changed.connect(self._on_w_moldb_changed)
        e0.loaded.connect(self._on_w_moldb_loaded)

        # Qt stuff tab #1: FileMolConsts editor
        e1 = self.w_molconsts = WFileMolConsts(self)

        # Qt stuff tab #2: FileConv editor TODO FileConv does not exist yet self.conv a Conv
        e2 = self.w_conv = _WConv(self)

        self.pages.append(ex.MyPage(text_tab="Molecular constants database",
                                    cls_save=ft.FileMolDB, clss_load=(ft.FileMolDB,), wild="*.sqlite", editor=e0, flag_autosave=True))

        self.pages.append(ex.MyPage(text_tab="Molecular constants",
                                    cls_save=ft.FileMolConsts, clss_load=(ft.FileMolConsts,), wild="*.py", editor=e1))

        self.pages.append(ex.MyPage(text_tab="Conversion",
                                    cls_save=ft.FileConfigConvMol, clss_load=(ft.FileConfigConvMol,), wild="*.py", editor=e2))

        self.setWindowTitle("(to) PFANT Molecular Lines Converter")
        self.installEventFilter(self)

    def eventFilter(self, obj_focused, event):
        if event.type() == QEvent.KeyPress:
            # To help my debugging: Configures for Kurucz OH conversion
            if event.key() == Qt.Key_F12:
                self.w_moldb.combobox_select_molecule.setCurrentIndex(7)
                self.w_moldb.combobox_select_pfantmol.setCurrentIndex(1)
                self.w_moldb.combobox_select_state.setCurrentIndex(6)
                self.w_moldb.combobox_select_system.setCurrentIndex(0)
                self.w_moldb.None_to_zero()
                self.w_source._buttons[2].setChecked(True)
                self.source_changed()
                self.w_kurucz.w_file.edit.setText("ohaxupdate.asc")
                self.tabWidget.setCurrentIndex(1)
        return False

    def _on_w_moldb_changed(self):
        self.w_molconsts.set_moldb(self.w_moldb.f)

    def _on_w_moldb_loaded(self):
        self.w_molconsts.set_moldb(self.w_moldb.f)

    def _on_w_molconsts_changed(self):
        print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")

    def _on_w_conv_changed(self):
        print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")

