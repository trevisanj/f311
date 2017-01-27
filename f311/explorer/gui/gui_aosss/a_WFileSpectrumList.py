__all__ = ["WFileSpectrumList"]

import collections
import copy
import matplotlib.pyplot as plt
from pylab import MaxNLocator
import numbers
import numpy as np
import os
import os.path
from itertools import product, combinations, cycle
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .a_WSpectrumCollection import *
import a99
from .... import explorer as ex
import f311.filetypes as ft


class WFileSpectrumList(a99.WBase):
    """
    FileSpectrumList editor widget.

    Arguments:
      parent=None
    """

    @property
    def menu_actions(self):
        return self.wsptable.menu_actions

    def __init__(self, parent):
        a99.WBase.__init__(self, parent)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        # Whether __update_f() went ok
        self.flag_valid = False
        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False
        # Whether there is sth in yellow background in the Headers tab
        self.flag_header_changed = False
        self.f = None  # FileSpectrumList object
        self.obj_square = None

        # # Central layout
        lantanide = self.centralLayout = QVBoxLayout()
        a99.set_margin(lantanide, 0)
        self.setLayout(lantanide)

        # ## Horizontal splitter occupying main area: (options area) | (plot area)
        sp2 = self.splitter2 = QSplitter(Qt.Horizontal)
        lantanide.addWidget(sp2)

        # ## Widget left of horizontal splitter, containing (File Line) / (Options area)
        wfilett0 = keep_ref(QWidget())
        lwfilett0 = QVBoxLayout(wfilett0)
        a99.set_margin(lwfilett0, 0)

        # ### Line showing the File Name
        wfile = keep_ref(QWidget())
        lwfilett0.addWidget(wfile)
        l1 = keep_ref(QHBoxLayout(wfile))
        a99.set_margin(l1, 0)
        l1.addWidget(keep_ref(QLabel("<b>File:<b>")))
        w = self.label_fn = QLabel()
        l1.addWidget(w)
        l1.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # ### Tabbed widget occupying left of horizontal splitter (OPTIONS TAB)
        tt0 = self.tabWidgetOptions = QTabWidget(self)
        lwfilett0.addWidget(tt0)
        tt0.setFont(a99.MONO_FONT)
        tt0.currentChanged.connect(self.current_tab_changed_options)

        # #### Tab: Vertical Splitter between "Place Spectrum" and "Existing Spectra"
        spp = QSplitter(Qt.Vertical)
        tt0.addTab(spp, "&Spectra")

        # # ##### Place Spectrum area
        # # Widget that will be handled by the scrollable area
        # sa0 = keep_ref(QScrollArea())
        # sa0.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # sa0.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # wscrw = keep_ref(QWidget())
        # sa0.setWidget(wscrw)
        # sa0.setWidgetResizable(True)
        # ###
        # lscrw = QVBoxLayout(wscrw)
        # a99.set_margin(lscrw, 3)
        # ###
        # alabel = keep_ref(QLabel("<b>Add spectrum</b>"))
        # lscrw.addWidget(alabel)
        # ###
        # # Place Spectrum variables & button
        # lg = keep_ref(QGridLayout())
        # lscrw.addLayout(lg)
        # a99.set_margin(lg, 0)
        # lg.setVerticalSpacing(4)
        # lg.setHorizontalSpacing(5)
        # # lscrw.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        #
        # # field map: [(label widget, edit widget, field name, short description, long description), ...]
        # map = self._map0 = []
        # ###
        # x = self.label_sp = QLabel()
        # y = self.choosesp = WChooseSpectrum()
        # y.installEventFilter(self)
        # y.edited.connect(self.on_colors_setup_edited)
        # # y.setValidator(QIntValidator())
        # x.setBuddy(y)
        # map.append((x, y, "&spectrum", ".dat, .fits ...", ""))
        #
        # for i, (label, edit, name, short_descr, long_descr) in enumerate(a99):
        #     # label.setStyleSheet("QLabel {text-align: right}")
        #     assert isinstance(label, QLabel)
        #     label.setText(a99.enc_name_descr(name, short_descr))
        #     label.setAlignment(Qt.AlignRight)
        #     lg.addWidget(label, i, 0)
        #     lg.addWidget(edit, i, 1)
        #     label.setToolTip(long_descr)
        #     edit.setToolTip(long_descr)
        #
        # # button
        # l = QHBoxLayout()
        # lscrw.addLayout(l)
        # a99.set_margin(l, 0)
        # l.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # b = QPushButton("&Place spectrum")
        # l.addWidget(b)
        # b.clicked.connect(self.add_spectrum_clicked)


        # ##### Spectrum Collection Editor area
        wex = QWidget()
        lwex = QVBoxLayout(wex)
        a99.set_margin(lwex, 3)
        # ###
        # lwex.addWidget(keep_ref(QLabel("<b>Existing spectra</b>")))
        ###
        w = self.wsptable = WSpectrumCollection(self.parent_form)
        w.edited.connect(self.on_spectra_edited)
        lwex.addWidget(w)

        # ##### Finally...
        # spp.addWidget(sa0)
        spp.addWidget(wex)

        # #### Headers tab
        sa1 = keep_ref(QScrollArea())
        tt0.addTab(sa1, "&Header")
        sa1.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        sa1.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Widget that will be handled by the scrollable area
        w = keep_ref(QWidget())
        sa1.setWidget(w)
        sa1.setWidgetResizable(True)
        lscrw = QVBoxLayout(w)
        a99.set_margin(lscrw, 3)
        ###
        lscrw.addWidget(keep_ref(QLabel("<b>Header properties</b>")))

        ###
        b = keep_ref(QPushButton("Collect field names"))
        b.clicked.connect(self.on_collect_fieldnames)
        lscrw.addWidget(b)

        # Form layout
        lg = keep_ref(QGridLayout())
        a99.set_margin(lg, 0)
        lg.setVerticalSpacing(4)
        lg.setHorizontalSpacing(5)
        lscrw.addLayout(lg)
        ###
        lscrw.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # field map: [(label widget, edit widget, field name, short description, long description, f_from_f, f_from_edit), ...]
        map = self._map1 = []

        ###
        x = keep_ref(QLabel())
        y = self.edit_fieldnames = QPlainTextEdit()
        y.textChanged.connect(self.on_header_edited)
        x.setBuddy(y)
        map.append((x, y, "&Field names", "'header' information for each spectrum", "", lambda: self.f.splist.fieldnames,
                   lambda: self.edit_fieldnames.toPlainText()))
        ###

        for i, (label, edit, name, short_descr, long_descr, f_from_f, f_from_edit) in enumerate(map):
            # label.setStyleSheet("QLabel {text-align: right}")
            assert isinstance(label, QLabel)
            label.setText(a99.enc_name_descr(name, short_descr))
            label.setAlignment(Qt.AlignRight)
            lg.addWidget(label, i, 0)
            lg.addWidget(edit, i, 1)
            label.setToolTip(long_descr)
            edit.setToolTip(long_descr)

        lgo = QHBoxLayout()
        a99.set_margin(lgo, 0)
        lscrw.addLayout(lgo)
        ###
        bgo = self.button_revert = QPushButton("Revert")
        lgo.addWidget(bgo)
        bgo.clicked.connect(self.header_revert)
        ###
        bgo = self.button_apply = QPushButton("Apply")
        lgo.addWidget(bgo)
        bgo.clicked.connect(self.header_apply)
        ###
        lgo.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # #### More Tools tab
        wset = keep_ref(QWidget())
        tt0.addTab(wset, "&More")
        lwset = keep_ref(QVBoxLayout(wset))
        ###
        la = keep_ref(QLabel("<b>Data manipulation</b>"))
        lwset.addWidget(la)
        ###
        b = keep_ref(QPushButton("&Crop in new window..."))
        lwset.addWidget(b)
        b.clicked.connect(self.crop_clicked)
        ###
        b = keep_ref(QPushButton("Add &noise..."))
        lwset.addWidget(b)
        b.clicked.connect(self.add_noise_clicked)
        ###
        b = keep_ref(QPushButton("&Upper envelopes"))
        lwset.addWidget(b)
        b.clicked.connect(self.rubberband_clicked)
        ###
        b = keep_ref(QPushButton("&Extract continua"))
        lwset.addWidget(b)
        b.clicked.connect(self.extract_continua_clicked)
        ###
        lwset.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # # ### Tabbed widget occupying right of horizontal splitter
        # tt1 = self.tabWidgetVis = QTabWidget(self)
        # tt1.setFont(a99.MONO_FONT)
        # tt1.currentChanged.connect(self.current_tab_changed_vis)
        #
        # # #### Tab containing 3D plot representation
        # w0 = keep_ref(QWidget())
        # tt1.addTab(w0, "&P")
        # # #### Colors tab
        # w1 = keep_ref(QWidget())
        # tt1.addTab(w1, "&Q")

        # ### Finally ...
        sp2.addWidget(wfilett0)
        # sp2.addWidget(tt1)


        self.setEnabled(False)  # disabled until load() is called
        a99.style_checkboxes(self)
        self.flag_process_changes = True
        self.add_log("Welcome from %s.__init__()" % (self.__class__.__name__))

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def load(self, x):
        assert isinstance(x, ft.FileSpectrumList)
        self.f = x
        self.wsptable.set_collection(x.splist)
        self.__update_gui(True)
        self.flag_valid = True  # assuming that file does not come with errors
        self.setEnabled(True)

    def update_splist_headers(self, splist):
        """Updates headers of a SpectrumList objects using contents of the Headers tab"""
        emsg, flag_error = "", False
        ss = ""
        flag_emit = False
        try:
            ss = "fieldnames"
            ff = a99.eval_fieldnames(str(self.edit_fieldnames.toPlainText()))
            splist.fieldnames = ff
            self.__update_gui(True)
            flag_emit = True
        except Exception as E:
            flag_error = True
            if ss:
                emsg = "Field '%s': %s" % (ss, a99.str_exc(E))
            else:
                emsg = a99.str_exc(E)
            self.add_log_error(emsg)
        if flag_emit:
            self.__emit_if()
        return not flag_error

    def update_gui_label_fn(self):
        self.__update_gui_label_fn()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        """Sets focus to first field. Note: reason is ignored."""

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def on_colors_setup_edited(self):
        if self.flag_process_changes:
            pass
            # self.flag_plot_colors_pending = True

    def on_header_edited(self):
        if self.flag_process_changes:
            sth = False
            sndr = self.sender()
            for _, edit, _, _, _, f_from_f, f_from_edit in self._map1:
                changed = f_from_f() != f_from_edit()
                sth = sth or changed
                if edit == sndr:
                    a99.style_widget_changed(self.sender(), changed)
            self.set_flag_header_changed(sth)

    def add_spectrum_clicked(self):
        flag_emit = False
        try:
            sp = self.choosesp.sp
            if not sp:
                raise RuntimeError("Spectrum not loaded")
            sp = copy.deepcopy(sp)
            self.f.splist.add_spectrum(sp)
            self.__update_gui()
            flag_emit = True
        except Exception as E:
            self.add_log_error(a99.str_exc(E), True)
            raise
        if flag_emit:
            self.edited.emit()

    def header_revert(self):
        self.__update_gui_header()

    def header_apply(self):
        if self.update_splist_headers(self.f.splist):
            self.__update_gui(True)

    def current_tab_changed_vis(self):
        pass
        # if self.flag_plot_colors_pending:
        #     self.plot_colors()

    def current_tab_changed_options(self):
        pass

    def crop_clicked(self):
        try:
            splist = self.f.splist
            specs = (("wavelength_range", {"value": "[%g, %g]" % (splist.wavelength[0], splist.wavelength[-1])}),)
            form = a99.XParametersEditor(specs=specs, title="Add Gaussian noise")
            while True:
                r = form.exec_()
                if not r:
                    break
                kk = form.get_kwargs()
                s = ""
                try:
                    s = "wavelength_range"
                    lambda0, lambda1 = eval(kk["wavelength_range"])
                except Exception as E:
                    self.add_log_error("Failed evaluating %s: %s" % (s, a99.str_exc(E)), True)
                    continue

                # Works with clone, then replaces original, to ensure atomic operation
                clone = copy.deepcopy(self.f)
                clone.filename = None
                try:
                    clone.splist.crop(lambda0, lambda1)
                except Exception as E:
                    self.add_log_error("Crop operation failed: %s" % a99.str_exc(E), True)
                    continue

                self.__new_window(clone)
                break

        except Exception as E:
            self.add_log_error("Crop failed: %s" % a99.str_exc(E), True)
            raise

    def rubberband_clicked(self):
        self.__use_sblock(ex.SB_Rubberband(flag_upper=True))

    def add_noise_clicked(self):
        specs = (("std", {"caption": "Noise standard deviation", "value": 1.}),)
        form = a99.XParametersEditor(specs=specs, title="Select sub-range")
        if form.exec_():
            block = ex.SB_AddNoise(**form.get_kwargs())
            self.__use_sblock(block)

    def extract_continua_clicked(self):
        self.__use_slblock(ex.SLB_ExtractContinua())

    # def std_clicked(self):
    #     self.__use_slblock(MergeDown(np.std))
    #
    # def snr_clicked(self):
    #     self.__use_slblock(GB_SNR())

    def on_collect_fieldnames(self):
        # TODO confirmation

        self.edit_fieldnames.setPlainText(str(self.f.splist.collect_fieldnames()))

    #        self.__update_gui(True)

    def on_spectra_edited(self, flag_changed_header):
        if flag_changed_header:
            self.__update_gui_header()
        self.__update_gui_vis()
        self.edited.emit()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear

    def __emit_if(self):
        if self.flag_process_changes:
            self.edited.emit()

    def __update_gui(self, flag_header=False):
        """Updates GUI to reflect what is in self.f"""
        self.flag_process_changes = False
        try:
            self.__update_gui_label_fn()
            self.wsptable.update()
            if flag_header:
                self.__update_gui_header()
        finally:
            self.flag_process_changes = True

    def __update_gui_label_fn(self):
        if not self.f:
            text = "(not loaded)"
        elif self.f.filename:
            text = os.path.relpath(self.f.filename, ".")
        else:
            text = "(filename not set)"
        self.label_fn.setText(text)

    def __update_gui_header(self):
        """Updates header controls only"""
        splist = self.f.splist
        self.edit_fieldnames.setPlainText(str(splist.fieldnames))
        self.set_flag_header_changed(False)

    def __update_gui_vis(self):
        pass

    def set_flag_header_changed(self, flag):
        self.button_apply.setEnabled(flag)
        self.button_revert.setEnabled(flag)
        self.flag_header_changed = flag
        if not flag:
            # If not changed, removes all eventual yellows
            for _, edit, _, _, _, _, _ in self._map1:
                a99.style_widget_changed(edit, False)

    def __update_f(self):
        self.flag_valid = self.update_splist_headers(self.f.splist)

    def __new_window(self, clone):
        """Opens new FileSparseCube in new window"""
        form1 = self.keep_ref(self.parent_form.__class__())
        form1.load(clone)
        form1.show()

    def __use_sblock(self, block):
        """Uses block and opens result in new window"""

        # Does not touch the original self.f
        clone = copy.deepcopy(self.f)
        clone.filename = None
        slblock = ex.SLB_UseSpectrumBlock()
        for i, sp in enumerate(clone.splist.spectra):
            clone.splist.spectra[i] = block.use(sp)
        self.__new_window(clone)

    def __use_slblock(self, block):
        """Uses block and opens result in new window"""
        # Here not cloning current spectrum list, but trusting the block
        block.flag_copy_wavelength = True
        output = block.use(self.f.splist)
        f = self.__new_from_existing()
        f.splist = output
        self.__new_window(f)

    def __new_from_existing(self):
        """Creates new FileSpectrumList from existing one"""
        f = ft.FileSpectrumList()
        return f

