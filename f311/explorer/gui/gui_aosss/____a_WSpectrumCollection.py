__all__ = ["WSpectrumCollection"]

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

# TODO options window to set this up
_CONFIG_LEGEND = "/gui/WSpectrumCollection/plot_overlapped/flag_legend"


class WSpectrumCollection(a99.WBase):
    """Editor for SpectrumCollection objects"""

    # argument0: flag_changed_header
    changed = pyqtSignal(bool)

    def __init__(self, parent):
        a99.WBase.__init__(self, parent)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        # Whether all the values in the fields are valid or not
        self.flag_valid = False
        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False
        self.collection = None # SpectrumCollection


        # # Creates actions

        action = self.action_all_group = QAction(a99.get_icon("group-by"), "&Group...", self)
        action.triggered.connect(self.on_all_group)


        # ## Makes a menu
        menu = self.menu_actions = QMenu("Spectrum &Collection")
        menu.addAction(self.action_add_spectra)
        m = keep_ref(menu.addMenu("With &All Spectra"))
        m.addAction(self.action_all_group)
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
        lwmain = self.centralLayout = QVBoxLayout()
        a99.set_margin(lwmain, 0)
        self.setLayout(lwmain)



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
        tb.addAction(self.action_all_group)
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

    def set_collection(self, x):
        assert isinstance(x, ft.SpectrumCollection)
        self.collection = x
        self.__update_gui()
        self.setEnabled(True)


    def get_selected_spectra(self):
        return [self.collection.spectra[i] for i in self.get_selected_spectrum_indexes()]


    def get_selected_row_indexes(self):
        ii = list(set([index.row() for index in self.twSpectra.selectedIndexes()]))
        return ii


    def get_selected_spectrum_indexes(self):
        items = self.twSpectra.selectedItems()
        ii = []
        for item in items:
            obj = item.data(1)
            if isinstance(obj, int):
                ii.append(obj)
        ii.sort()
        return ii


    def row_index_to_spectrum_index(self, row_index):
        """
        Converts table row index within self.collection.spectra

        This is necessary because the table may be sorted
        """

        item = self.twSpectra.item(row_index, self.twSpectra.columnCount()-1)
        ret = item.data(1)
        return ret


    def get_current_spectrum_index(self):
        row_index = self.twSpectra.currentRow()
        if row_index == -1:
            return -1
        return self.row_index_to_spectrum_index(row_index)


    def get_current_spectrum(self):
        """Returns spectrum on which the table cursor (movable with the keyboar arrows) is currently"""
        spectrum_index = self.get_current_spectrum_index()
        if spectrum_index == -1:
            return None
        return self.collection.spectra[spectrum_index]

    def update(self):
        """Refreshes the GUI to reflect what is in self.collection"""
        self.__update_gui()

    def is_spectrum_list(self):
        """Returns True if self.collection is a ft.SpectrumList

        Collection is either a ft.SpectrumList or ft.SparseCube"""
        return isinstance(self.collection, ft.SpectrumList)

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        """Sets focus to first field. Note: reason is ignored."""
        self.twSpectra.setFocus()


    def eventFilter(self, source, event):
        if event.type() == QEvent.FocusIn:
            # text = random_name()
            # self.__add_log(text)
            pass

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                if source == self.twSpectra:
                    n_deleted = self.__delete_spectra()
                    if n_deleted > 0:
                        self.changed.emit(False)
        return False

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def section_moved(self, idx_logical, idx_vis_old, idx_vis_new):
        obj = self.collection
        l = self.collection.fieldnames_visible
        fieldname_current = l[idx_vis_old]
        del l[idx_vis_old]
        l.insert(idx_vis_new, fieldname_current)


    def show_header_context_menu(self, position):
        obj = self.collection

        ah = self.twSpectra.horizontalHeader()
        # col_idx = ah.logicalIndexAt(position)
        col_idx = ah.visualIndex(ah.logicalIndexAt(position))

        menu = QMenu()
        act_hide_current = None
        fieldname_current = None

        if col_idx < len(obj.fieldnames_visible):
            fieldname_current = obj.fieldnames_visible[col_idx]
            act_hide_current = menu.addAction("&Hide field '%s'" % fieldname_current)
            menu.addSeparator()

        act_show_all = menu.addAction("&Show all fields")
        act_hide_all = menu.addAction("&Hide all fields")
        act_restore_order = menu.addAction("&Restore order")
        menu.addSeparator()

        aa_visible = []
        for fieldname in obj.fieldnames:
            act = menu.addAction(fieldname)
            act.setCheckable(True)
            act.setChecked(fieldname in obj.fieldnames_visible)
            aa_visible.append(act)

        action = menu.exec_(self.twSpectra.mapToGlobal(position))
        flag_update = False
        if action == act_hide_current and fieldname_current is not None:
            obj.fieldnames_visible.remove(fieldname_current)
            flag_update = True

        elif action == act_show_all:
            for fieldname in reversed(obj.fieldnames):
                if not fieldname in obj.fieldnames_visible:
                    obj.fieldnames_visible.insert(0, fieldname)
                    flag_update = True

        elif action == act_hide_all:
            obj.fieldnames_visible = []
            flag_update = True

        elif action == act_restore_order:
            curr_visible = copy.copy(obj.fieldnames_visible)
            obj.fieldnames_visible = []
            for fieldname in obj.fieldnames:
                if fieldname in curr_visible:
                    obj.fieldnames_visible.append(fieldname)
            flag_update = not (curr_visible == obj.fieldnames_visible)

        elif action in aa_visible:
            idx = aa_visible.index(action)
            if not aa_visible[idx].isChecked():
                obj.fieldnames_visible.remove(obj.fieldnames[idx])
            else:
                obj.fieldnames_visible.insert(0, obj.fieldnames[idx])
            flag_update = True

        if flag_update:
            self.__update_gui()
            self.changed.emit(False)


    def on_twSpectra_customContextMenuRequested(self, position):
        """Mounts, shows popupmenu for the tableWidget control, and takes action."""
        obj = self.collection
        menu = QMenu()
        act_del = menu.addAction("&Delete selected (Del)")

        action = menu.exec_(self.twSpectra.mapToGlobal(position))
        flag_update = False
        if action == act_del:
            n_deleted = self.__delete_spectra()
            if n_deleted > 0:
                self.changed.emit(False)

        if flag_update:
            self.changed.emit(False)
            self.__update_gui()


    def on_all_group(self):
        from f311 import explorer as ex

        # Import here to circumvent cyclic dependency
        from .a_XGroupSpectra import XGroupSpectra
        form = XGroupSpectra()

        if not form.exec_():
            return

        # It sth fails, will restore original
        save = copy.deepcopy(self.collection)
        try:
            grouper = ex.blocks.slb.SLB_UseGroupBlock(form.block, form.group_by)
            self.collection = grouper.use(self.collection)
            self.__update_gui()
            flag_emit = True
        except Exception as E:
            # Restores and logs error
            self.collection = save
            self.add_log_error("Failed to transform spectra: %s" % str(E), True)
            raise

        if flag_emit:
            self.changed.emit(True)

    #
    # def on_all_use_spectrum_block(self):
    #     flag_emit, flag_changed_header = False, False
    #
    #     from .a_XUseSpectrumBlock import XUseSpectrumBlock
    #     form = self.keep_ref(XUseSpectrumBlock())
    #     if not form.exec_():
    #         return
    #
    #     # It sth fails, will restore original
    #     save = copy.deepcopy(self.collection)
    #     try:
    #         sspp = save.spectra
    #         self.collection.clear()
    #         for sp in sspp:
    #             block = copy.deepcopy(form.block)
    #             self.collection.add_spectrum(block.use(sp))
    #
    #         self.__update_gui()
    #         flag_emit = True
    #
    #     except Exception as E:
    #         # Restores and logs error
    #         self.collection = save
    #         self.add_log_error("Failed to transform spectra: %s" % str(E), True)
    #         raise
    #
    #     if flag_emit:
    #         self.changed.emit(True)


    def on_all_to_scalar(self):
        flag_emit, flag_changed_header = False, False

        from .a_XToScalar import XToScalar
        form = self.keep_ref(XToScalar())
        if not form.exec_():
            return

        # It sth fails, will restore original
        save = copy.deepcopy(self.collection)
        try:
            for sp in self.collection.spectra:
                sp.more_headers[form.fieldname] = form.block.use(sp)

            if not form.fieldname in self.collection.fieldnames:
                self.collection.fieldnames.insert(0, form.fieldname)

            if not form.fieldname in self.collection.fieldnames_visible:
                self.collection.fieldnames_visible.insert(0, form.fieldname)

            self.__update_gui()
            flag_emit = True

        except Exception as E:
            # Restores and logs error
            self.add_log_error("Failed to extract scalar: %s" % str(E), True)
            self.collection = save
            raise

        if flag_emit:
            self.changed.emit(True)


    def on_plot_xy(self):
        # Import here to circumvent cyclic dependency
        from .a_XPlotXY import XPlotXY
        form = self.keep_ref(XPlotXY(self.collection))
        form.show()


    def on_plot_xyz(self):
        # Import here to circumvent cyclic dependency
        from .a_XPlotXYZ import XPlotXYZ
        form = self.keep_ref(XPlotXYZ(self.collection))
        form.show()


    def on_all_export_csv(self):
        new_filename = QFileDialog.getSaveFileName(self, "Export text file (CSV format)", "export.csv", "*.csv")[0]
        if new_filename:
            # self.save_dir, _ = os.path.split(str(new_filename))
            try:
                lines = self.collection.to_csv()
                with open(str(new_filename), "w") as file:
                    file.writelines(lines)
            except Exception as E:
                msg = str("Error exporting text file: %s" % a99.str_exc(E))
                self.add_log_error(msg, True)
                raise


    def on_sel_use_spectrum_block(self):
        flag_emit, flag_changed_header = False, False

        from .a_XUseSpectrumBlock import XUseSpectrumBlock
        form = self.keep_ref(XUseSpectrumBlock())
        if not form.exec_():
            return

        # It sth fails, will restore original
        save = copy.deepcopy(self.collection)
        try:
            sspp = self.get_selected_spectra()
            self.collection.delete_spectra(self.get_selected_spectrum_indexes())
            for sp in sspp:
                block = copy.deepcopy(form.block)
                self.collection.add_spectrum(block.use(sp))

            self.__update_gui()
            flag_emit = True

        except Exception as E:
            # Restores and logs error
            self.collection = save
            self.add_log_error("Failed to transform spectra: %s" % str(E), True)
            raise

        if flag_emit:
            self.changed.emit(True)


    def on_sel_plot_stacked(self):
        from f311 import explorer as ex

        sspp = self.get_selected_spectra()
        if len(sspp) > 0:
            ex.plot_spectra(sspp)


    def on_sel_plot_overlapped(self):
        from f311 import explorer as ex

        sspp = self.get_selected_spectra()
        flag_legend = ex.get_config().get_item(_CONFIG_LEGEND, True)
        oo = ex.PlotSpectrumSetup(flag_legend=flag_legend)
        if len(sspp) > 0:
            ex.plot_spectra_overlapped(sspp, setup=oo)


    def on_sel_open_in_new(self):
        ii = self.get_selected_spectrum_indexes()
        if len(ii) > 0:
            other = copy.deepcopy(self.collection)
            other.spectra = [copy.deepcopy(other.spectra[i]) for i in ii]
            # TODO who said it is a spectrum list? Could well be a FileSparseCube!!!! How to sort this?????????????????????????????????????????????????????????????????????

            # "Gambiarra"
            if self.is_spectrum_list():
                from .a_XFileSpectrumList import XFileSpectrumList
                f = ft.FileSpectrumList()
                form = self.keep_ref(XFileSpectrumList())
            else:
                from .a_XFileSparseCube import XFileSparseCube
                f = ft.FileSparseCube()
                f.sparsecube = other
                form = self.keep_ref(XFileSparseCube())

            # f.filename = "noname"

            form.load(f)
            form.show()


    def on_sel_delete(self):
        n = self.__delete_spectra()
        if n > 0:
            self.changed.emit(False)


    def on_curr_scale(self):
        """Performs a scaling operation on the current spectrum"""
        sp = self.get_current_spectrum()

        if sp is None:
            return

        form = XScaleSpectrum()
        form.set_spectrum(sp)
        if form.exec_():
            k = form.factor()
            if k != 1:
                sp.y *= k
                self.__update_gui()
                self.changed.emit(False)


    def on_twSpectra_cellChanged(self, row, column):
        """Cell has been changed manually: commit to self.collection"""
        if self.flag_process_changes:
            flag_emit = False
            text = None
            item = self.twSpectra.item(row, column)
            name = self.__get_tw_header(column)
            self.flag_process_changes = False
            try:
                value = str(item.text())
                # Tries to convert to float, otherwise stores as string
                try:
                    value = float(value)
                except:
                    pass

                # Certain fields must evaluate to integer because they are pixel positions
                if name in ("PIXEL-X", "PIXEL-Y", "Z-START"):
                    value = int(value)

                # Units must be a valid astropy.Unit() argument
                if name in ("X-UNIT", "Y-UNIT"):
                    value = u.Unit(value)

                spectrum_index = self.row_index_to_spectrum_index(row)

                self.collection.spectra[spectrum_index].more_headers[name] = value

                flag_emit = True
                # replaces changed text with eventually cleaner version, e.g. decimals from integers are discarded
                item.setText(str(value))

            except Exception as E:
                # restores original value
                item.setText(str(self.collection.spectra[row].more_headers.get(name)))
                self.add_log_error(a99.str_exc(E), True)
                raise

            finally:
                self.flag_process_changes = True

            if flag_emit:
                self.changed.emit(False)


    def on_twSpectra_itemSelectionChanged(self):
        """Updates actions enabled state"""
        self.__update_enabled_actions()


    def on_add_spectra(self):
        flag_emit = False
        filenames = QFileDialog.getOpenFileNames(self, "Add Spectra", "",
         "All files(*.*);;Spectrum List files (*.splist);;Sparse Cube files (*.sparsecube)")[0]
        if not filenames:
            return

        # classes = ft.classes_sp()+[ft.FileSpectrumList, ft.FileSparseCube]
        classes = ft.classes_collection()
        report, successful, failed = ["<b>Results</b>"], [], []
        for filename in filenames:
            filename = str(filename)
            basename = os.path.basename(filename)
            file = ft.load_with_classes(filename, classes)
            try:
                if file is None:
                    raise RuntimeError("Could not load file")
                if isinstance(file, ft.FileSpectrum):
                    self.collection.add_spectrum(file.spectrum)
                elif isinstance(file, ft.FileSpectrumList):
                    self.collection.merge_with(file.splist)
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

            self.__update_gui()
            flag_emit = True

        if len(failed) > 0:
            report.extend(["", "Failed:"])
            report.extend(failed)

        if flag_emit:
            self.changed.emit(False)

        a99.show_message("<br>".join(report))


    # def on_merge_with(self):
    #     flag_emit = False
    #     try:
    #         # TODO another SpectrumCollection, not SpectrumList
    #         new_filename = QFileDialog.getOpenFileName(self, "Merge with another Spectrum List file", "", "*.splist")[0]
    #         if new_filename:
    #             new_filename = str(new_filename)
    #             f = ft.FileSpectrumList()
    #             f.load(new_filename)
    #             self.collection.merge_with(f.splist)
    #             self.__update_gui()
    #             flag_emit = True
    #     except Exception as E:
    #         msg = "Error merging: %s" % a99.str_exc(E)
    #         self.add_log_error(msg, True)
    #         raise
    #
    #     if flag_emit:
    #         self.changed.emit(False)
    #


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear


    def __get_tw_header(self, column):
        return str(self.twSpectra.horizontalHeaderItem(column).text())


    def __update_gui(self):
        """Updates GUI to match self.collection, i.e., mainly the table widget"""

        self.flag_process_changes = False
        try:
            # Builds table widget contents
            spectra = self.collection.spectra
            t = self.twSpectra
            n = len(spectra)
            FIXED = ["Spectrum summary report"]
            fieldnames_visible = self.collection.fieldnames_visible
            all_headers = fieldnames_visible+FIXED
            nc = len(all_headers)
            a99.reset_table_widget(t, n, nc)
            t.setHorizontalHeaderLabels(all_headers)
            i = 0
            for sp in spectra:
                j = 0

                # Spectrum.more_headers columns
                for h in fieldnames_visible:
                    twi = QTableWidgetItem(str(sp.more_headers.get(h)))
                    if h in "Z-START":  # fields that should be made read-only
                        twi.setFlags(twi.flags() & ~Qt.ItemIsEditable)
                    t.setItem(i, j, twi)
                    j += 1

                # Spectrum self-generated report
                twi = QTableWidgetItem(sp.one_liner_str())
                twi.setFlags(twi.flags() & ~Qt.ItemIsEditable)
                # stores spectrum index not to lose track in case the table is sorted by column
                twi.setData(1, i)
                t.setItem(i, j, twi)
                j += 1

                i += 1

            t.resizeColumnsToContents()

        finally:
            self.__update_enabled_actions()

            self.flag_process_changes = True

    def __update_enabled_actions(self):
        can_group = isinstance(self.collection, ft.SpectrumList)
        has_any = self.twSpectra.rowCount() > 0
        any_selected = len(self.twSpectra.selectedItems()) > 0
        has_current = self.twSpectra.currentRow() > -1

        self.action_add_spectra.setEnabled(True)
        self.action_all_group.setEnabled(can_group and has_any)
        self.action_all_to_scalar.setEnabled(has_any)
        self.action_all_export_csv.setEnabled(has_any)
        self.action_sel_use_spectrum_block.setEnabled(any_selected)
        self.action_sel_plot_stacked.setEnabled(any_selected)
        self.action_sel_plot_overlapped.setEnabled(any_selected)
        self.action_sel_open_in_new.setEnabled(any_selected)
        self.action_sel_delete.setEnabled(any_selected)
        self.action_curr_scale.setEnabled(has_current)
