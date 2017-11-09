__all__ = ["WSparseCube"]

import copy
import os
import os.path
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .a_XScaleSpectrum import *
from astropy import units as u
import a99
# from .... import explorer as ex
import f311.filetypes as ft
from .a_WSpectrumCollectionBase import *
import f311


class WSparseCube(WSpectrumCollectionBase):
    """Editor for SparseCube objects"""

    # argument0: flag_changed_header
    changed = pyqtSignal(bool)

    def __init__(self, parent):
        WSpectrumCollectionBase.__init__(self, parent, True)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False

        # # Creates actions

        # ## Makes a menu
        menu = self.menu_actions = QMenu("Spectrum &List")
        menu.addAction(self.action_add_spectra)
        m = keep_ref(menu.addMenu("With &All Spectra"))
        # m.addAction(self.action_sel_use_spectrum_block)
        m.addAction(self.action_all_to_scalar)
        m.addAction(self.action_all_plot_xy)
        m.addAction(self.action_all_plot_xyz)
        m.addAction(self.action_all_export_csv)
        m = keep_ref(menu.addMenu("With &Selected Spectra"))
        m.addAction(self.action_sel_use_spectrum_block)
        m.addAction(self.action_sel_plot_stacked)
        m.addAction(self.action_sel_plot_overlapped)
        m.addAction(self.action_sel_open_in_new)
        m.addAction(self.action_sel_delete)
        m = keep_ref(menu.addMenu("With &Current Spectrum"))
        m.addAction(self.action_curr_scale)


        # # Central layout
        # Will have a toolbox and a table. When the toolbox contracts, there is more space for the table
        lwmain = self.layout_editor
        a99.set_margin(lwmain, 0)
        self.setLayout(lwmain)

        lxy = self.keep_ref(QHBoxLayout())
        lwmain.addLayout(lxy)


        x = self.keep_ref(QLabel("<b>To add spectra:</b>"))
        lxy.addWidget(x)

        x = self.label_x = QLabel("x-coordinate")
        y = self.spinbox_x = QSpinBox()
        y.setToolTip("x-coordinate to add spectra to cube (in pixels; 0-based)")
        # y.valueChanged.connect(self.on_place_spectrum_edited)
        y.setMinimum(0)
        y.setMaximum(1000)
        x.setBuddy(y)
        lxy.addWidget(x)
        lxy.addWidget(y)

        x = self.label_y = QLabel("x-coordinate")
        y = self.spinbox_y = QSpinBox()
        y.setToolTip("y-coordinate to add spectra to cube (in pixels; 0-based)")
        # y.valueChanged.connect(self.on_place_spectrum_edited)
        y.setMinimum(0)
        y.setMaximum(1000)
        x.setBuddy(y)
        lxy.addWidget(x)
        lxy.addWidget(y)

        lxy.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # ## Toolbox
        # The toolbox will have only one widget whose layout is a grid with two columns:
        #   - The first column contains labels
        #   - The second column contains panels of buttons layed horizontally


        wtoolboxes = keep_ref(a99.WCollapsiblePanel())
        lwmain.addWidget(wtoolboxes)
        wtoolboxes.label.setText("<b>Tools</b>")
        wtoolboxes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # ### Layout to have (grid layout, spacer)
        lwtoolboxes = QHBoxLayout(wtoolboxes.widget)
        lwmain.addLayout(lwtoolboxes)
        a99.set_margin(lwtoolboxes, 0)
        lwtoolboxes.setSpacing(0)

        # #### Grid layour
        lg = QGridLayout()
        lwtoolboxes.addLayout(lg)
        a99.set_margin(lg, 2)
        lg.setSpacing(0)
        label = keep_ref(QLabel('<b>File:</b>'))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lg.addWidget(label, 0, 0)
        label = keep_ref(QLabel('<b>With all:</b>'))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lg.addWidget(label, 1, 0)
        label = keep_ref(QLabel('<b>With selected:</b>'))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lg.addWidget(label, 2, 0)
        label = keep_ref(QLabel('<b>With current:</b>'))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lg.addWidget(label, 3, 0)


        TOOL_BUTTON_STYLE = Qt.ToolButtonTextBesideIcon
        # TOOL_BUTTON_STYLE = Qt.ToolButtonIconOnly


        # ##### Toolbar #0: operations independent of the table widget selection state
        ###
        tb = self.toolBar0 = QToolBar()
        lg.addWidget(tb, 0, 1)
        tb.setToolButtonStyle(TOOL_BUTTON_STYLE)
        tb.addAction(self.action_add_spectra)
        tb.setIconSize(QSize(16, 16))

        # ##### Toolbar #1: operations independent of the table widget selection state
        ###
        tb = self.toolBar1 = QToolBar()
        lg.addWidget(tb, 1, 1)
        tb.setToolButtonStyle(TOOL_BUTTON_STYLE)
        tb.setIconSize(QSize(16, 16))
        tb.addAction(self.action_all_to_scalar)
        tb.addAction(self.action_all_plot_xy)
        tb.addAction(self.action_all_plot_xyz)
        tb.addAction(self.action_all_export_csv)


        # ##### Toolbar #2: operations affecting only the spectra which are selected
        ###
        tb = self.toolBar2 = QToolBar()
        lg.addWidget(tb, 2, 1)
        tb.setIconSize(QSize(16, 16))
        tb.setToolButtonStyle(TOOL_BUTTON_STYLE)
        tb.addAction(self.action_sel_use_spectrum_block)
        tb.addAction(self.action_sel_plot_stacked)
        tb.addAction(self.action_sel_plot_overlapped)
        tb.addAction(self.action_sel_open_in_new)
        tb.addAction(self.action_sel_delete)

        # ##### Toolbar #3: operations affecting only the current spectrum
        ###

        tb = self.toolBar3 = QToolBar()
        lg.addWidget(tb, 3, 1)
        tb.setIconSize(QSize(16, 16))
        tb.setToolButtonStyle(TOOL_BUTTON_STYLE)
        tb.addAction(self.action_curr_scale)

        # #### Spacer
        lwtoolboxes.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))


        # ## Table Widget
        a = self.twSpectra = QTableWidget()
        lwmain.addWidget(a)
        a.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        a.setSelectionMode(QAbstractItemView.MultiSelection)
        a.setSelectionBehavior(QAbstractItemView.SelectRows)
        a.setAlternatingRowColors(True)
        a.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        a.setFont(a99.MONO_FONT)
        a.installEventFilter(self)
        a.setContextMenuPolicy(Qt.CustomContextMenu)
        a.customContextMenuRequested.connect(self.on_twSpectra_customContextMenuRequested)
        a.setSortingEnabled(True)
        a.cellChanged.connect(self.on_twSpectra_cellChanged)
        a.itemSelectionChanged.connect(self.on_twSpectra_itemSelectionChanged)
        ah = a.horizontalHeader()
        ah.setSectionsMovable(True)
        ah.setContextMenuPolicy(Qt.CustomContextMenu)
        ah.customContextMenuRequested.connect(self.show_header_context_menu)
        ah.setSelectionMode(QAbstractItemView.SingleSelection)
        ah.sectionMoved.connect(self.section_moved)


        # # Final adjustments
        self.setEnabled(False)  # disabled until load() is called
        a99.style_checkboxes(self)
        self.flag_process_changes = True
        self.add_log("Welcome from %s.__init__()" % (self.__class__.__name__))


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def get_pixel_xy(self):
        x = int(self.spinbox_x.value())
        if not (0 <= x < self.collection.width):
            raise RuntimeError("x must be in [0, %s)" % self.collection.width)
        y = int(self.spinbox_y.value())
        if not (0 <= y < self.collection.height):
            raise RuntimeError("y must be in [0, %s)" % self.collection.height)
        return x, y


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def on_add_spectra(self):
        flag_emit = False
        filenames = QFileDialog.getOpenFileNames(self, "Add Spectra", "",
         "All files(*.*);;Spectrum List files (*.splist);;Sparse Cube files (*.sparsecube)")[0]
        if not filenames:
            return

        # classes = f311.classes_sp()+[ft.FileSpectrumList, ft.FileSparseCube]
        classes = f311.classes_collection()
        report, successful, failed = ["<b>Results</b>"], [], []
        for filename in filenames:
            filename = str(filename)
            basename = os.path.basename(filename)
            file = ft.load_with_classes(filename, classes)
            try:
                if file is None:
                    raise RuntimeError("Could not load file")
                if isinstance(file, ft.FileSpectrum):
                    self.collection.add_spectrum(file.spectrum, *self.get_pixel_xy())
                elif isinstance(file, ft.FileSpectrumList):
                    self.collection.merge_with(file.splist, *self.get_pixel_xy())
                elif isinstance(file, ft.FileSparseCube):
                    self.collection.merge_with(file.sparsecube)
                successful.append("  - %s" % basename)
            except Exception as e:
                failed.append('&nbsp;&nbsp;- %s: %s' % (basename, str(e)))
                s = "Error adding file '%s': %s" % (basename, a99.str_exc(e))
                a99.get_python_logger().exception(s)
                self.add_log_error(s)

        if len(successful) > 0:
            report.extend(["", "Successful:"])
            report.extend(successful)

            # # "Gambiarra" to expose field names
            # if not self.is_spectrum_list():
            #     c = self.collection
            #     ffnn, aann = ["PIXEL-X", "PIXEL-Y"], ["fieldnames", "fieldnames_visible"]
            #     for fn in ffnn:
            #         for an in aann:
            #             a = c.__getattribute__(an)
            #             if fn not in a:
            #                 a.append(fn)

            self._update_gui()
            flag_emit = True

        if len(failed) > 0:
            report.extend(["", "Failed:"])
            report.extend(failed)

        if flag_emit:
            self.changed.emit(False)

        a99.show_message("<br>".join(report))


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear


    def _update_enabled_actions(self):
        has_any = self.twSpectra.rowCount() > 0
        any_selected = len(self.twSpectra.selectedItems()) > 0
        has_current = self.twSpectra.currentRow() > -1

        self.action_add_spectra.setEnabled(True)
        self.action_all_to_scalar.setEnabled(has_any)
        self.action_all_export_csv.setEnabled(has_any)
        self.action_sel_use_spectrum_block.setEnabled(any_selected)
        self.action_sel_plot_stacked.setEnabled(any_selected)
        self.action_sel_plot_overlapped.setEnabled(any_selected)
        self.action_sel_open_in_new.setEnabled(any_selected)
        self.action_sel_delete.setEnabled(any_selected)
        self.action_curr_scale.setEnabled(has_current)
