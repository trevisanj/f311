# todo plot "X" instead of line
# rename molecule


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT # as NavigationToolbar2QT
import matplotlib.pyplot as plt
import numpy as np
from .a_XMolLinesEditor import *
import os.path
import webbrowser
import sys
from ._shared import *
import a99
import f311.filetypes as ft


__all__ = ["XFileMolecules"]


NUM_PLOTS = len(SOL_HEADERS_PLOT)-1  # -1 because whe "lambda" does not have its plot


class XFileMolecules(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.f = None  # FileMolecules object
        self.flag_sort = False
        self.mol_index = None
        self.sol_index = None
        self.mol = None
        self.sol = None
        self.save_dir = "."
        self.flag_changed = False
        self.form_lines = None

        # Information about the plots
        self.marker_row = None  # points into current set-of-lines, self.sol
        self.plot_info = [PlotInfo() for _ in range(NUM_PLOTS)]
        self.set_flag_plot(SOL_ATTR_NAMES.index("sj")-1, True)
        self.set_flag_plot(SOL_ATTR_NAMES.index("jj")-1, True)

        # ** tab "General file info"
        a = self.plainTextEditFileInfo = QPlainTextEdit()
        a.setFont(a99.MONO_FONT)


        # ** "Molecules browser"

        # ** ** left of splitter
        self.labelMol = QLabel('Molecules list (Ctrl+1)')
        a = self.listWidgetMol = QListWidget()
        a.currentRowChanged.connect(self.on_listWidgetMol_currentRowChanged)
        # a.setEditTriggers(QAbstractItemView.DoubleClicked)
        # a.setEditTriggers(QAbstractItemView.AllEditTriggers)
        a.setContextMenuPolicy(Qt.CustomContextMenu)
        a.customContextMenuRequested.connect(self.on_listWidgetMol_customContextMenuRequested)
        a.itemDoubleClicked.connect(self.on_listWidgetMol_doubleClicked)
        a.installEventFilter(self)

        l = self.layoutMol = QVBoxLayout()
        a99.set_margin(l, 0)
        l.setSpacing(1)
        l.addWidget(self.labelMol)
        l.addWidget(self.listWidgetMol)

        a = self.widgetMol = QWidget()
        a.setLayout(self.layoutMol)


        # ** ** right of splitter

        # ** ** ** tab "Molecule info"
        a = self.plainTextEditMolInfo = QPlainTextEdit()
        a.setFont(a99.MONO_FONT)

        # ** ** ** tab "Molecular lines"

        # ** ** ** ** left

        # P = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.labelSol = QLabel('Sets of lines (Ctrl+2)')

        a = self.listWidgetSol = QListWidget()
        a.setFont(a99.MONO_FONT)
        # a.setFixedWidth(100)
        a.currentRowChanged.connect(self.on_listWidgetSol_currentRowChanged)
        a.setContextMenuPolicy(Qt.CustomContextMenu)
        a.customContextMenuRequested.connect(self.on_listWidgetSol_customContextMenuRequested)
        a.itemDoubleClicked.connect(self.on_listWidgetSol_doubleClicked)
        a.installEventFilter(self)

        l = self.layoutSol = QVBoxLayout()
        a99.set_margin(l, 0)
        l.setSpacing(1)
        l.addWidget(self.labelSol)
        l.addWidget(self.listWidgetSol)

        a = self.widgetSol = QWidget()
        a.setLayout(self.layoutSol)

        # ** ** ** ** right

        # ** ** ** ** ** Toolbar above plot

        am = self.buttonSort = QPushButton("Sort wave (Alt+&W)")
        am.clicked.connect(self.on_buttonSort_clicked)
        am.setCheckable(True)
        am.setToolTip("Sort spectral lines in ascending order of wavelength")
        if self.flag_sort:
            am.setChecked(True)

        # adds checkable buttons sj, jj
        self.plot_buttons = bb = []
        for i in range(NUM_PLOTS):  # sj, jj etc
            s = SOL_HEADERS[i+1]
            b = QPushButton("%s (Alt+&%d)" % (s, i+1))
            b.clicked.connect(self.on_button_plot_clicked)
            b.setCheckable(True)
            if self.flag_plot(i):
                b.setChecked(True)
            bb.append(b)

        a11 = self.buttonEditLines = QPushButton("Edit lines (Ctrl+3)")
        a11.clicked.connect(self.on_buttonEditLines_clicked)
        a2 = self.labelNumLines = QLabel("--")
        a3 = self.spacer0 = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        l0 = self.layoutSolToolbar = QHBoxLayout()
        l0.addWidget(am)
        for b in bb:
            l0.addWidget(b)
        l0.addWidget(a11)
        l0.addWidget(a2)
        l0.addItem(a3)
        a99.set_margin(l0, 1)
        a = self.widgetSolToolbar = QWidget()
        a.setLayout(l0)
        a.setFixedHeight(40)

        # ** ** ** ** ** Set-of-lines info + Plot TABS

        # ** ** ** ** ** ** tab "Set-of-lines info"
        a = self.plainTextEditSolInfo = QPlainTextEdit()
        a.setFont(a99.MONO_FONT)

        # ** ** ** ** ** ** Plot tab

        # http://stackoverflow.com/questions/12459811
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('button_press_event', self.on_plot_click)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        a99.set_margin(layout, 0)

        a = self.widgetSolPlot = QWidget()
        a.setLayout(layout)

        l1 = self.layoutSolPlot = QVBoxLayout()
        l1.addWidget(self.widgetSolToolbar)
        l1.addWidget(self.widgetSolPlot)
        a99.set_margin(l1, 0)

        a = self.widgetSolPlot = QWidget()
        a.setLayout(l1)


        # ** ** ** ** **  Set-of-lines info + Plot TABS
        a = self.tabWidgetSol = QTabWidget(self)
        a.addTab(self.plainTextEditSolInfo, "Set-of-lines Info (Alt+&N)")
        a.addTab(self.widgetSolPlot, "Set-of-lines plots (Alt+&P)")
        a.setCurrentIndex(1)
        a.setFont(a99.MONO_FONT)

        # ** ** ** ** ** splitter: (list of set-of-lines) | (plot)
        a = self.splitterSol = QSplitter(Qt.Horizontal)
        a.addWidget(self.widgetSol)
        a.addWidget(self.tabWidgetSol)
        a.setStretchFactor(0, 2)
        a.setStretchFactor(1, 10)

        a = self.tabWidgetMol = QTabWidget()
        a.addTab(self.plainTextEditMolInfo, "Molecule info (Alt+&M)")
        a.addTab(self.splitterSol, "Sets of lines (Alt+&L)")
        a.setCurrentIndex(1)
        a.setFont(a99.MONO_FONT)

        # ** splitter: (list of molecules) | (molecules tab widget)
        a = self.splitterMol = QSplitter(Qt.Horizontal)
        a.addWidget(self.widgetMol)
        a.addWidget(self.tabWidgetMol)
        a.setStretchFactor(0, 2)
        a.setStretchFactor(1, 10)

        # tab "File" (main tab widget
        a = self.tabWidgetFile = QTabWidget(self)
        a.addTab(self.plainTextEditFileInfo, "General File Info (Alt+&I)")
        a.addTab(self.splitterMol, "Molecules Browser (Alt+&B)")
        a.setCurrentIndex(1)
        a.setFont(a99.MONO_FONT)


        # * # * # * # * # * # * # *
        # Now the menu bar

        # self.menubar = QMenuBar(self)
        # self.menubar.setGeometry(QRect(0, 0, 772, 18))
        # self.menubar.setObjectName(_fromUtf8("menubar"))
        b = self.menuBar()
        m = self.menu_file = b.addMenu("&File")
        self.act_save = ac = m.addAction("&Save")
        ac.setShortcut("Ctrl+S")
        ac.triggered.connect(self.on_save)
        self.act_save_as = ac = m.addAction("Save &as...")
        ac.setShortcut("Ctrl+Shift+S")
        ac.triggered.connect(self.on_save_as)
        m.addSeparator()
        ac = m.addAction("&Quit")
        ac.setShortcut("Ctrl+Q")
        ac.triggered.connect(self.close)

        # * # * # * # * # * # * # *
        # Final adjustments

        self.setCentralWidget(self.tabWidgetFile)
        a99.place_left_top(self)

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #

    def keyPressEvent(self, ev):
        if ev.modifiers() == Qt.ControlModifier:
            k = ev.key()
            if k == Qt.Key_1:
                self.listWidgetMol.setFocus()
            elif k == Qt.Key_2:
                self.listWidgetSol.setFocus()
            elif k == Qt.Key_3:
                self.on_buttonEditLines_clicked()

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return:
                if source == self.listWidgetMol:
                    self.edit_mol()
                    return True
                if source == self.listWidgetSol:
                    self.edit_sol()
                    return True
            if event.key() == Qt.Key_Delete:
                if source == self.listWidgetMol:
                    self.delete_mol()
                    return True
        return False

    def closeEvent(self, event):
        if self.flag_changed:
            # http://straightedgelinux.com/blog/python/html/pyqtxt.html
            r = QMessageBox.question(self,
                        "About to exit",
                        "File \"%s\" has unsaved changes. Save now?" % self.f.filename,
                        QMessageBox.Yes | QMessageBox.No|
                        QMessageBox.Cancel)
            if r == QMessageBox.Cancel:
                event.ignore()
            else:
                if r == QMessageBox.No:
                    pass
                elif r == QMessageBox.Yes:
                    try:
                        self.save()
                    except:
                        # In case of error saving file, will not exit the program
                        event.ignore()
        if event.isAccepted():
            self.close_editor()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Slots

    def on_help(self, _):
        try:
            base_dir = os.path.dirname(sys.argv[0])
            webbrowser.open_new(os.path.join(base_dir, "mled.html"))
            a99.show_message("Help file mled.html was opened in web browser.")
        except Exception as e:
            a99.show_error(str(e))

    def on_save(self, _):
        self.disable_save_actions()
        try:
            self.save()
        except Exception as e:
            a99.show_error(str(e))
        finally:
            self.enable_save_actions()

    def on_save_as(self, _):
        self.disable_save_actions()
        try:
            if self.f:
                new_filename = QFileDialog.getSaveFileName(self, "Save file",
                 self.save_dir, "*.dat")[0]
                if new_filename:
                    self.save_dir, _ = os.path.split(str(new_filename))
                    self.save_as(new_filename)
        except Exception as e:
            a99.show_error(str(e))
        finally:
            self.enable_save_actions()

    def on_listWidgetMol_currentRowChanged(self, row):
        if row > -1:
            self.set_molecule(row)

    def on_listWidgetSol_currentRowChanged(self, row):
        if row > -1:
            self.set_sol(row)

    def on_button_plot_clicked(self):
        # This may be triggered by any of the plot buttons
        button = self.sender()
        idx = self.plot_buttons.index(button)
        self.set_flag_plot(idx, button.isChecked())
        self.plot_lines()

    def on_buttonSort_clicked(self):
        self.flag_sort = self.buttonSort.isChecked()
        self.plot_lines()

    def on_listWidgetMol_customContextMenuRequested(self, position):
        menu = QMenu()
        a_edit = menu.addAction("&Edit")
        a_delete = menu.addAction("&Delete")
        action = menu.exec_(self.listWidgetMol.mapToGlobal(position))
        if action == a_edit:
            self.edit_mol()
        elif action == a_delete:
            self.delete_mol()

    def on_listWidgetSol_customContextMenuRequested(self, position):
        menu = QMenu()
        a_edit = menu.addAction("&Edit")
        action = menu.exec_(self.listWidgetSol.mapToGlobal(position))
        if action == a_edit:
            self.edit_sol()

    def on_listWidgetMol_doubleClicked(self):
        self.edit_mol()

    def on_listWidgetSol_doubleClicked(self):
        self.edit_sol()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #

    def load(self, f):
        """Loads file into GUI."""
        assert isinstance(f, ft.FileMolecules)

        self.f = f

        self.plainTextEditFileInfo.setPlainText(str(f))

        for m in f.molecules:
            assert isinstance(m, ft.Molecule)
            item = QListWidgetItem(self.get_mol_string(m))
            # not going to allow editing yet item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.listWidgetMol.addItem(item)

        if len(f.molecules) > 0:
            self.listWidgetMol.setCurrentRow(0)

        self.flag_changed = False
        self.update_window_title()

    def save(self):
        if self.f:
            self.f.save_as()
            self.flag_changed = False
            self.update_window_title()

    def save_as(self, filename):
        if self.f:
            self.f.save_as(filename)
            self.flag_changed = False
            self.update_window_title()

    def set_molecule(self, i):
        self.mol_index = i
        m = self.mol = self.f.molecules[i] if len(self.f.molecules) > i else None

        self.update_mol_info()

        w = self.listWidgetSol
        w.clear()

        if m is not None:
            for i, sol in enumerate(m.sol):
                item = QListWidgetItem(self.get_sol_string(i, sol))
                w.addItem(item)

            if len(m) > 0:
                w.setCurrentRow(0)

    def set_sol(self, j):
        self.sol_index = j
        self.sol = self.f.molecules[self.mol_index].sol[j]
        self.update_sol_info()
        self.plot_lines()
        self.set_editor_sol()

    def plot_lines(self):
        try:
            self.clear_markers()
            o = self.sol
            if o is not None:
                self.figure.clear()

                n = sum([info.flag for info in self.plot_info])  # number of subplots (0, 1 or 2)
                # map to reuse plotting routine, contains what differs between each plot

                map_ = [(SOL_HEADERS_PLOT[i], o.__getattribute__(SOL_ATTR_NAMES[i]))
                        for i in range(1, len(SOL_HEADERS_PLOT))]

                i_subplot = 1
                for i in range(len(map_)):
                    y_label = map_[i][0]
                    pi = self.plot_info[i]
                    pi.y_vector = _y = map_[i][1]

                    if pi.flag:
                        if not self.flag_sort:
                            x = o.lmbdam
                            y = _y
                        else:
                            _x = np.array(o.lmbdam)
                            _y = np.array(_y)
                            ii = np.argsort(_x)
                            x = _x[ii]
                            y = _y[ii]

                        a99.format_BLB()

                        self.figure.add_subplot(n, 1, i_subplot)
                        pi.axis = ax = self.figure.gca()
                        ax.clear()
                        ax.plot(x, y, 'k'+('' if len(x) > 1 else 'x'))
                        ax.set_xlabel('Wavelength ($\AA$)')
                        ax.set_ylabel(y_label)

                        # x-limits
                        xmin, xmax = min(x), max(x)
                        k = .02*(xmax-xmin)
                        ax.set_xlim([xmin-k, xmax+k])

                        # y-limits
                        ymin, ymax = min(y), max(y)
                        k = .02*(ymax-ymin)
                        ax.set_ylim([ymin-k, ymax+k])

                        i_subplot += 1

                if i_subplot > 1:
                    plt.tight_layout()

                self.canvas.draw()
                self.draw_markers()
        except Exception as e:
            a99.show_error("Error drawing plots: {}".format(str(e)))


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #

    def edit_mol(self):
        obj = self.mol
        if obj is None:
            return
        item = self.listWidgetMol.currentItem()
        r, form = a99.show_edit_form(obj,
            ["description", "symbols", "fe", "do", "mm", "am", "bm", "ua", "ub", "te", "cro", "s"],
            item.text())
        flag_changed = False
        if r == QDialog.Accepted:
            kwargs = form.get_kwargs()
            for name, value in kwargs.items():
                orig = obj.__getattribute__(name)
                if orig != value:
                    obj.__setattr__(name, value)
                    flag_changed = True
        if flag_changed:
            self.flag_changed = True
            item.setText(self.get_mol_string(obj))
            # item.setStyleSheet("selected:active{background: yellow}")
            # item.setTextColor(QColor(255, 0, 0))
            # item.setBackgroundColor(QColor(255, 0, 0))
            self.update_mol_info()
            self.update_window_title()

    def delete_mol(self):
        f = self.f
        if f is None:
            return
        i = self.listWidgetMol.currentRow()
        if i >= len(f.molecules):
            return
        del self.f.molecules[i]
        self.listWidgetMol.takeItem(i)
        self.flag_changed = True
        self.update_window_title()


    def edit_sol(self):
        obj = self.sol
        if obj is None:
            return
        item = self.listWidgetSol.currentItem()
        r, form = a99.show_edit_form(self.sol, ["vl", "v2l", "qqv", "ggv", "bbv", "ddv", "fact"],
                                    item.text())
        flag_changed = False
        if r == QDialog.Accepted:
            kwargs = form.get_kwargs()
            for name, value in kwargs.items():
                orig = obj.__getattribute__(name)
                if orig != value:
                    obj.__setattr__(name, value)
                    flag_changed = True
        if flag_changed:
            self.flag_changed = True
            item.setText(self.get_sol_string(self.listWidgetSol.currentRow(), obj))
            # item.setTextColor(QColor(255, 0, 0))
            self.update_sol_info()
            self.update_window_title()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #

    def update_mol_info(self):
        """Makes report for the current molecule."""
        m = self.mol
        s = str(m)
        # No need to repeat this information, already shown in listWidgetSol
        # s += '\n\n' \
        # 'Sets of lines\n' \
        #      '-------------\n' \
        #      ' # Number of lines\n'
        # for i in range(len(m)):
        #     s += '%2d %15d\n' % (i+1, len(m.lmbdam[i]))
        self.plainTextEditMolInfo.setPlainText(s)

    def update_sol_info(self):
        """Makes report for the current set-of-lines."""
        o = self.sol
        s = str(o)
        self.plainTextEditSolInfo.setPlainText(s)
        n = len(o)
        self.labelNumLines.setText('Number of lines: %d' % (n,))

    def update_window_title(self):
        self.setWindowTitle("mled - %s" % (self.f.filename+("" if not self.flag_changed
                                                            else " (changed)"),))

    def enable_save_actions(self):
        self.act_save.setEnabled(True)
        self.act_save_as.setEnabled(True)

    def disable_save_actions(self):
        self.act_save.setEnabled(False)
        self.act_save_as.setEnabled(False)


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Routines related to the lines editor

    def on_buttonEditLines_clicked(self):
        if self.form_lines is None:
            f = self.form_lines = XMolLinesEditor(self)
            f.show()
            self.set_editor_sol()
        self.plot_lines()

    def MolLinesEditor_closing(self):
        """Called by the molecular lines editor to notify that it is closing."""
        self.form_lines = None
        self.marker_row = None
        self.plot_lines()  # to remove the "X" from the plot

    def MolLinesEditor_current_row_changed(self, currentRow):
        """Called by the molecular lines editor to notify that the current row has changed."""
        self.set_marker_row(currentRow)

    def MolLinesEditor_cell_changed(self, row, column, value):
        """Called by the molecular lines editor to notify that a value has changed."""
        attr_name = SOL_ATTR_NAMES[column]
        v = self.sol.__getattribute__(attr_name)
        if v[row] != value:
            v[row] = value
            self.flag_changed = True
            self.plot_lines()
            self.update_window_title()

    def set_editor_sol(self):
        """Sets the set-of-lines of the editor."""
        if self.sol is not None and self.form_lines is not None:
            self.form_lines.set_sol(self.sol, "Set-of-lines: "+
                                    self.listWidgetSol.currentItem().text())

    def close_editor(self):
        if self.form_lines is not None:
            self.form_lines.close()

    # Controlling plots and markers for current row

    def set_marker_row(self, i):
        self.clear_markers()
        self.marker_row = i
        self.draw_markers()

    def clear_markers(self):
        for o in self.plot_info:
            if o.mpl_obj:
                a99.remove_line(o.mpl_obj)
                o.mpl_obj = None

    def draw_markers(self):
        self.clear_markers()
        if self.marker_row is not None and any([o.flag for o in self.plot_info]):
            i = self.marker_row
            lambda_ = self.sol.lmbdam[i]
            for o in self.plot_info:
                if o.flag:
                    # http://stackoverflow.com/questions/22172565/matplotlib-make-plus-sign-thicker
                    o.mpl_obj = o.axis.plot([lambda_], [o.y_vector[i]], 'xr', mew=2, ms=10)
            self.canvas.draw()

    def flag_plot(self, idx):
        return self.plot_info[idx].flag

    def set_flag_plot(self, idx, x):
        self.plot_info[idx].flag = x

    def on_plot_click(self, event):
        lambda_ = event.xdata
        if lambda_ is not None and self.form_lines is not None:
            idx = a99.index_nearest(self.sol.lmbdam, lambda_)
            self.form_lines.set_row(idx)
            # self.set_marker_row(idx)

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #

    @staticmethod
    def get_mol_string(m):
        return m.description

    @staticmethod
    def get_sol_string(index, sol):
        return "%3d %7s" % (index+1, '(%d)' % len(sol))
