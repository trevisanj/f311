__all__ = ["WSpectrumCollectionBase"]

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
_CONFIG_LEGEND = "/gui/WSpectrumCollectionBase/plot_overlapped/flag_legend"


class WSpectrumCollectionBase(a99.WEditor):
    """Base class for WSpectrumList and WSparseCube

    This class implements some operations that are the same for either WSpectrumList and WSparseCube

    This class does not implement the visual stuff.
    """


    def __init__(self, parent, flag_splist=True):
        a99.WEditor.__init__(self, parent)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        self.collection = None # SpectrumCollection
        self.flag_splist = flag_splist


        # # Creates actions

        action = self.action_add_spectra = QAction(a99.get_icon("list-add"), "&Add spectra...", self)
        action.setToolTip("Opens a 'Open File' window where multiple files can be selected.\n"
                          "Accepts any supported spectral type, and also other Spectrum Collection files.\n"
                          "Files are added in alphabetical order.")
        action.triggered.connect(self.on_add_spectra)

        action = self.action_all_to_scalar = QAction(a99.get_icon("go-next"), "To &Scalar...", self)
        action.triggered.connect(self.on_all_to_scalar)

        action = self.action_all_plot_xy = QAction(a99.get_icon("visualization"), "X-&Y Plot", self)
        action.triggered.connect(self.on_plot_xy)

        action = self.action_all_plot_xyz = QAction(a99.get_icon("visualization"), "X-Y-&Z Plot", self)
        action.triggered.connect(self.on_plot_xyz)

        action = self.action_all_export_csv = QAction(a99.get_icon("document-export"), "&Export CSV...", self)
        action.triggered.connect(self.on_all_export_csv)

        action = self.action_sel_use_spectrum_block = QAction(a99.get_icon("go-next"), "&Transform...", self)
        action.setToolTip("Selected spectra will be deleted and transformed spectra will be added at the end")
        action.triggered.connect(self.on_sel_use_spectrum_block)

        action = self.action_sel_plot_stacked = QAction(a99.get_icon("chart2"), "Plot &Stacked", self)
        action.triggered.connect(self.on_sel_plot_stacked)

        action = self.action_sel_plot_overlapped = QAction(a99.get_icon("chart1"), "Plot &Overlapped", self)
        action.triggered.connect(self.on_sel_plot_overlapped)

        action = self.action_sel_open_in_new = QAction(a99.get_icon("window-new"), "Open in new window", self)
        action.triggered.connect(self.on_sel_open_in_new)

        action = self.action_sel_delete = QAction(a99.get_icon("list-remove"), "Delete", self)
        action.triggered.connect(self.on_sel_delete)

        action = self.action_curr_scale = QAction(a99.get_icon("zoom-fit"), "Scale to Magnitude...", self)
        action.triggered.connect(self.on_curr_scale)



    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def set_collection(self, x):
        assert isinstance(x, ft.SpectrumCollection)
        self.collection = x
        self._update_gui()
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
        self._update_gui()


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
                    n_deleted = self._delete_spectra()
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
            self._update_gui()
            self.changed.emit(False)

    def on_twSpectra_customContextMenuRequested(self, position):
        """Mounts, shows popupmenu for the tableWidget control, and takes action."""
        obj = self.collection
        menu = QMenu()
        act_del = menu.addAction("&Delete selected (Del)")

        action = menu.exec_(self.twSpectra.mapToGlobal(position))
        flag_update = False
        if action == act_del:
            n_deleted = self._delete_spectra()
            if n_deleted > 0:
                self.changed.emit(False)

        if flag_update:
            self.changed.emit(False)
            self._update_gui()

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

            self._update_gui()
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

            self._update_gui()
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
            if self.flag_splist:
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
        n = self._delete_spectra()
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
                self._update_gui()
                self.changed.emit(False)


    def on_twSpectra_cellChanged(self, row, column):
        """Cell has been changed manually: commit to self.collection"""
        if self.flag_process_changes:
            flag_emit = False
            text = None
            item = self.twSpectra.item(row, column)
            name = self._get_tw_header(column)
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
                # replaces edited text with eventually cleaner version, e.g. decimals from integers are discarded
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
        self._update_enabled_actions()


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear


    def _get_tw_header(self, column):
        return str(self.twSpectra.horizontalHeaderItem(column).text())


    def _update_gui(self):
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
            self._update_enabled_actions()

            self.flag_process_changes = True

    def _delete_spectra(self):
        ii = self.get_selected_spectrum_indexes()
        if len(ii) > 0:
            self.collection.delete_spectra(ii)
            self._update_gui()

        return len(ii)
