"""Explorer window."""
__all__ = ["XExplorer"]

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
import f311
import os
import glob
import os.path
import time
import matplotlib.pyplot as plt
import numpy as np
# from .. import *


COLOR_LOADED = "#ADFFB4"  # light green
COLOR_LOAD_ERROR = "#FFB5B5"  # light red
COLOR_DIR = "#FFFFB5"  # light yellow
# Maximum size of file to be loaded automatically (in bytes)
MAX_FILESIZE_AUTO_LOAD = 1.2*2**20


@a99.froze_it
class _FileProps(object):
    def __init__(self):
        # DataFile object or None
        self.f = None
        # string or None
        self.filepath = None
        # Already "scanned" (load attempted)
        self.flag_scanned = False
        # Error loading?
        self.flag_error = False
        # Is text?
        self.flag_text = False
        # Is file (name to match os.path.isfile
        self.isfile = False
        # Error message
        self.error_message = ""
        # Row index in table
        self.row_index = None
        # Date changed
        self.mtime = None

    def get_color(self):
        """Returns None if background not to be changed, otherwise a QColor."""
        if not self.isfile:
            return QColor(COLOR_DIR)
        elif not self.flag_scanned:
            return None
        elif self.flag_error:
            return QColor(COLOR_LOAD_ERROR)
        return QColor(COLOR_LOADED)

    def get_summary(self):
        ret = "File not scanned yet"
        if not self.isfile:
            ret = '<span style="color: #B38600">Directory</span>'
        elif self.flag_scanned:
            ll = ["text file" if self.flag_text else "binary file"]
            if self.flag_error:
                emsg = self.error_message or "file type not recognized"
                ll.append("<span style=\"font-weight: bold; color: {0!s}\">{1!s}</span>".format(a99.COLOR_ERROR, emsg))
            else:
                ll.append("<span style=\"color: {0!s}\">File type: <b>{1!s}</b></span>".format("#006000", self.f.__class__.__name__))
            ret = ("; ".join(ll))
        return ret

    def get_info(self):
        ret = ""
        if self.flag_scanned and not self.flag_error:
            ret = str(self.f)
        return ret

class LoadThread(QThread):
    def __init__(self, parent, propss, cls=None):
        # cls: specific class to use
        QThread.__init__(self, parent)
        self.propss = propss
        self.cls = cls

    def run(self):
        for props in self.propss:
            if not props.isfile:
                continue
            f = None
            try:
                if self.cls:
                    f = self.cls()
                    f.load(props.filepath)
                else:
                    f = f311.load_any_file(props.filepath)
                props.f = f
            except Exception as e:
                # Suppresses exceptions
                props.error_message = str(e)
                a99.get_python_logger().exception("Loading file '{}'".format(props.filepath))
                f = None
            finally:
                props.flag_scanned = True
                props.flag_error = f is None
                props.flag_text = a99.is_text_file(props.filepath)

#
# class VisThread(QThread):
#     def __init__(self, parent, vis_class, props):
#         QThread.__init__(self, parent)
#         self.vis_class = vis_class
#         self.props = props
#         self.form = parent
#
#     def run(self):
#         vis_class = self.vis_class
#         props = self.props
#         if vis_class == "txt":
#             w = XText(self.form, open(props.filepath, "r").read(), props.filepath)
#             w.show()
#         else:
#             vis_class().use(props.f)

###############################################################################


class XExplorer(QMainWindow):
    """"F311 Explorer" window

    Args:
      parent=None
      dir_=".": directory name
      _flag_set_dir=True: will not set directory if False (testing purpose only)
    """

    def __init__(self, parent=None, dir_=".", _flag_set_dir=True):
        QMainWindow.__init__(self, parent)
        self.dir = None
        # Whether to close matplotlib plots when window is closed
        self.flag_close_mpl_plots_on_close = True
        self.__vis_classes = []
        # List of (DataFile objects)/(None if not loaded)/(-1 if error loading)
        self.__propss = []
        # # More internals
        self.__flag_loading = False
        self.__flag_visualizing = False
        self.__flag_updating_table = False
        self.__load_thread = None
        self.__flag_creating = True
        self.__lock_propss = a99.MyLock(flag_verbose=False)

        # # Timer to watch for changed files
        t = self.timer_changed = QTimer()
        t.setInterval(1000)  # miliseconds
        t.timeout.connect(self.on_timer_changed_timeout)
        t.start()


        # # Menu bar
        b = self.menuBar()
        m = self.menu_file = b.addMenu("&File")
        ac = self.action_load = m.addAction("Attempt &load")
        ac.setShortcut("Ctrl+L;Ctrl+O")
        ac.triggered.connect(self.on_load)
        ac = self.action_load_as = m.addAction("Load &As...")
        ac.setShortcut("Alt+A")
        ac.triggered.connect(self.on_load_as)
        m.addSeparator()
        ac = m.addAction("&Refresh")
        ac.setShortcut("Ctrl+R")
        ac.triggered.connect(self.on_refresh)
        m.addSeparator()
        ac = m.addAction("Change &directory...")
        ac.setShortcut("Ctrl+D")
        ac.triggered.connect(self.on_cd)
        m.addSeparator()
        ac = m.addAction("&Quit")
        ac.setShortcut("Ctrl+Q")
        ac.triggered.connect(self.close)

        m = self.menu_tools = b.addMenu("&Tools")
        accw = m.addAction("&Collect errors")
        accw.triggered.connect(self.on_collect_errors)

        # # Status bar
        self.labelStatus = QLabel("Welcome")
        sb = self.statusBar()
        sb.insertWidget(0, self.labelStatus, 0)


        # # Central widget

        cw = self.centralWidget = QWidget()
        lcw = self.centralLayout = QVBoxLayout(cw)
        a99.set_margin(lcw, 1)

        # ## Toolbar
        l0 = self.layoutToolbar = QHBoxLayout()


        a0 = self.c88532 = QLabel("<b>&Directory:</b>")
        l0.addWidget(a0)
        #
        a1 = self.lineEditDir = QLineEdit()
        l0.addWidget(a1)
        a1.installEventFilter(self)  # we want _down arrow_ to jump to table widget
        a0.setBuddy(a1)
        a1.returnPressed.connect(self.on_cd2)
        #
        w = self.line44412 = QFrame() # vertical line
        l0.addWidget(w)
        # w.setGeometry(QRect(240, 240, 3, 61))
        w.setFrameShape(QFrame.VLine)
        w.setFrameShadow(QFrame.Sunken)
        w.setFixedWidth(3)
        #
        b6 = self.pushButtonCollectErrors = QPushButton("&Collect errors")
        b6.setToolTip("Searches for errors in log files and reports these errors in a new window.")
        b6.clicked.connect(accw.triggered)
        l0.addWidget(b6)
        #
        lcw.addLayout(l0)



        # # Horizontal splitter
        # Containis a table on the left and a "possibilities are" on the right

        sp = self.splitter = QSplitter(Qt.Horizontal)

        # ## File listing table

        w = self.cdf856 = QWidget()
        l0 = self.c49g7s = QVBoxLayout(w)
        a99.set_margin(l0, 0)
        #
        y = self.c88ss8 = QLabel("<b>Directory &contents</b>")
        l0.addWidget(y)
        #
        t = self.tableWidget = QTableWidget()
        y.setBuddy(t)
        l0.addWidget(t)
        t.installEventFilter(self)
        # t.setSelectionBehavior(QAbstractItemView.SelectRows)
        # t.currentCellChanged.connect(self.on_tableWidget_currentCellChanged)
        t.cellDoubleClicked.connect(self.on_tableWidget_cellDoubleClicked)
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setFont(a99.MONO_FONT)
        t.resizeColumnsToContents()
        t.installEventFilter(self)
        t.selectionModel().selectionChanged.connect(self.selectionChanged)
        t.setContextMenuPolicy(Qt.CustomContextMenu)
        t.customContextMenuRequested.connect(self.on_tableWidget_customContextMenuRequested)

        sp.addWidget(w)

        # ## "Possibilities area"
        # The area is a widget that will be added to the main splitter.
        # The area will contain a vertical layout with two widgets: a label
        # and another splitter.

        w = QWidget()
        sp.addWidget(w)
        l1 = QVBoxLayout(w)
        a99.set_margin(l1, 0)

        # ### Label containing information about the current selection in the table widget

        y = self.c77ww8 = QLabel("<b>Brief</b>")
        l1.addWidget(y)

        x = self.labelSummary = QLabel()
        l1.addWidget(x)

        # ### Splitter containing a "visualization options area"
        #     and a "general file info" area
        s0 = QSplitter(Qt.Vertical)
        l1.addWidget(s0)

        # #### "visualization options" area
        w = self.csslff = QWidget()
        s0.addWidget(w)
        l1 = self.c49378 = QVBoxLayout(w)
        a99.set_margin(l1, 0)
        y = self.c88888 = QLabel("<b>&Actions available for selected file(s)</b>")
        l1.addWidget(y)
        x = self.listWidgetVis = QListWidget(self)
        x.installEventFilter(self)
        x.itemDoubleClicked.connect(self.on_listWidgetVis_itemDoubleClicked)
        y.setBuddy(x)

        l1.addWidget(x)

        # #### "general file info" area
        w = self.c77777 = QWidget()
        s0.addWidget(w)
        l1 = self.c86888 = QVBoxLayout(w)
        a99.set_margin(l1, 0)
        x = self.c83388 = QLabel("<b>Data file &information</b>")
        x.setToolTip("The box below will show information only if the file is of a "
                     "supported type")
        l1.addWidget(x)
        x = self.textEditInfo = QTextEdit(self)
        self.c83388.setBuddy(x)
        l1.addWidget(x)
        x.setReadOnly(True)
        x.setFont(a99.MONO_FONT)

        lcw.addWidget(sp)
        self.setCentralWidget(cw)
        s0.setStretchFactor(0, 3)
        s0.setStretchFactor(1, 10)

        if _flag_set_dir:
            self.set_dir(dir_)

        self.__flag_creating = False

        a99.place_center(self, 1000, 620)

    def set_dir(self, dir_):
        """Sets directory, auto-loads, updates all GUI contents."""

        self.__lock_set_dir(dir_)
        self.__lock_auto_load()
        self.__lock_update_table()
        self.__update_info()
        self.__update_window_title()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # *
    # Qt override

    def eventFilter(self, obj, event):
        if self.__flag_creating:
            return False

        if obj == self.tableWidget:
            if a99.check_return_space(event, self.on_load):
                return True
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Up:
                    if self.tableWidget.currentRow() == 0:
                        self.lineEditDir.setFocus()
        elif obj == self.listWidgetVis:
            return a99.check_return_space(event, self.__visualize)
        elif obj == self.lineEditDir:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Down:
                    self.tableWidget.setFocus()
        return False

    def closeEvent(self, event):
        if self.flag_close_mpl_plots_on_close:
            plt.close("all")

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # *
    # Slots

    def on_tableWidget_cellDoubleClicked(self, row, col):
        # Assuming that double-click will also select the row of the file to load
        self.on_load()

    def on_listWidgetVis_itemDoubleClicked(self, item):
        # Assuming that double-click will also select the row
        try:
            self.__visualize()
        except Exception as e:
            a99.show_error(str(e))
            raise

    def on_tableWidget_customContextMenuRequested(self, position):
        menu = QMenu()
        menu.addAction(self.action_load)
        menu.addAction(self.action_load_as)
        action = menu.exec_(self.tableWidget.mapToGlobal(position))

    def selectionChanged(self, *args):
        if self.__flag_updating_table:
            return
        self.__update_info()

    def on_load(self, _=None):
        if not self.__flag_loading:
            pp = self.__lock_get_current_propss()
            if len(pp) == 1 and not pp[0].isfile:
                self.set_dir(pp[0].filepath)
            else:
                self.__lock_load()

    def on_load_as(self, _=None):
        if not self.__flag_loading:
            pp = self.__lock_get_current_propss()
            if len(pp) == 1 and not pp[0].isfile:
                return
            else:
                form = f311.XSelectDataFile()
                if form.exec_():
                    self.__lock_load(form.cls)

    def on_refresh(self, _=None):
        if not self.__flag_loading:
            self.set_dir(self.dir)

    def on_cd(self, _=None):
        if not self.__flag_loading:
            dir_ = QFileDialog.getExistingDirectory(None, "Change directory", self.dir)[0]
            if dir_:
                self.set_dir(str(dir_))

    def on_cd2(self):
        new_dir = str(self.lineEditDir.text())
        if os.path.isdir(new_dir):
            new_dir = os.path.abspath(new_dir)
            self.set_dir(new_dir)
        else:
            a99.show_error("Invalid directory")

    def on_collect_errors(self, _=None):
        if self.__flag_loading:
            return

        from f311 import explorer as ex

        self.__flag_loading = True
        self.__set_status_text("Collecting errors, please wait...")
        try:
            k = a99.ErrorCollector()
            k.collect_errors(self.dir)
            w = ex.XHTML(self, k.get_html(), "Errors in '{0!s}' and subdirectories".format(self.dir))
            w.show()
        except Exception as e:
            MSG = "Could not collect errors"
            a99.get_python_logger().exception(MSG)
            a99.show_error("{0!s}: {1!s}".format(MSG, str(e)))
        finally:
            self.__flag_loading = False
            self.__set_status_text("")

    def on_timer_changed_timeout(self):
        if self.__flag_loading:
            return
        self.__lock_check_dir_contents_changed()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # *
    # Internals

    def __update_window_title(self):
        full_dir = os.path.abspath(self.dir)
        self.setWindowTitle("F311 Explorer")
        self.lineEditDir.setText(full_dir)

    def __get_current_vis_class(self):
        return self.__vis_classes[self.listWidgetVis.currentRow()]

    def __update_info(self):
        """Updates "visualization options" and "file info" areas."""

        from f311 import explorer as ex
        import f311

        t = self.tableWidget
        z = self.listWidgetVis
        z.clear()
        classes = self.__vis_classes = []
        propss = self.__lock_get_current_propss()
        npp = len(propss)
        s0, s1 = "", ""
        if npp == 1:
            p = propss[0]
            # Visualization options
            if p.flag_scanned:
                if isinstance(p.f, f311.DataFile):
                    classes.extend(f311.get_suitable_vis_classes(p.f))
                    if ex.VisPrint in classes:
                        classes.remove(ex.VisPrint)
                if p.flag_text:
                    # This is an exception, since "txt" is not a Vis descendant.
                    # This will be properly handled in __visualize()
                    classes.append("txt")

                for x in classes:
                    if x == "txt":
                        text = "View plain text"
                    else:
                        text = x.action
                        text += " ("+x.__name__+")"
                    item = QListWidgetItem(text)
                    z.addItem(item)

            # File info
            s0 = p.get_summary()
            s1 = p.get_info()

        elif npp >= 2:
            s0 = "{0:d} selected".format(npp)
            ff = [p.f for p in propss]
            flag_spectra = all([isinstance(f, f311.FileSpectrum) for f in ff])

            # gambiarra to visualize several PFANT .mod files
            has_pyfant = False
            try:
                import pyfant
                has_pyfant = True
            except:
                pass

            flag_mod = False
            if has_pyfant:
                flag_mod = all([isinstance(f, pyfant.FileModBin) and len(f.records) > 1 for f in ff])

            if flag_spectra:
                z.addItem(QListWidgetItem("Plot spectra stacked"))
                classes.append("sta")
                z.addItem(QListWidgetItem("Plot spectra overlapped"))
                classes.append("ovl")
            elif flag_mod:

                # TODO plugin-based way to handle visualization of multiple selection

                z.addItem(QListWidgetItem("View model grid"))
                classes.append("modgrid")
                
        # File info
        self.labelSummary.setText(s0)
        self.textEditInfo.setPlainText(s1)



    def __set_status_text(self, text):
        self.labelStatus.setText(text)
        QApplication.instance().processEvents()

    def __visualize(self):
        from f311 import explorer as ex
        self.__flag_visualizing = True
        self.__set_status_text("Creating visualization, please wait...")
        try:
            vis_class = self.__get_current_vis_class()
            if vis_class == "ovl":
                propss = self.__lock_get_current_propss()
                spectra = [p.f.spectrum for p in propss]
                ex.plot_spectra_overlapped(spectra)
            elif vis_class == "sta":
                propss = self.__lock_get_current_propss()
                spectra = [p.f.spectrum for p in propss]
                ex.plot_spectra_stacked(spectra)
            elif vis_class == "modgrid":
                propss = self.__lock_get_current_propss()
                models = [p.f for p in propss]
                ex.plot_mod_grid(models)
            else:
                props = self.__lock_get_current_props()
                if vis_class == "txt":
                    w = ex.XText(self, open(props.filepath, "r").read(), props.filepath)
                    w.show()
                else:
                    vis_class().use(props.f)
        finally:
            self.__set_status_text("")
            self.__flag_visualizing = False
        # t = VisThread(self, self.__get_current_vis_class(), self.__get_current_props())
        # t.finished.connect(self.__finished_visualizing)
        # t.start()

    def __finished_loading(self):
        self.__set_status_text("")
        self.__flag_loading = False
        t = self.tableWidget
        row = t.currentRow()
        for props in self.__load_thread.propss:
            i, c = props.row_index, props.get_color()
            for j in range(t.columnCount()):
                t.item(i, j).setBackground(c)
        self.__update_info()

    # def __finished_visualizing(self):
    #     self.__set_status_text("")
    #     self.__flag_visualizing = False

    def __get_auto_size(self):
        # Returns the number of bytes that will be automatically analysed.
        return 100.*2**20  # 100 MB


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # *
    # Internals mutually locked: __lock*()

    def __lock_update_table(self):
        self.__flag_updating_table = True
        try:
            with self.__lock_propss:
                n = len(self.__propss)

                t = self.tableWidget
                a99.reset_table_widget(t, n, 3)
                t.setHorizontalHeaderLabels(["filename", "size", "date modified"])

                for i, p in enumerate(self.__propss):
                    p.row_index = i

                    items = []
                    info = os.stat(p.filepath)
                    filename = os.path.basename(p.filepath)
                    # if not p.isfile:
                    #     filename = "["+filename+"]"
                    item = QTableWidgetItem(filename)
                    items.append(item)
                    t.setItem(i, 0, item)
                    item = QTableWidgetItem(str(info.st_size))
                    items.append(item)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                    t.setItem(i, 1, item)
                    item = QTableWidgetItem(time.ctime(info.st_mtime))
                    items.append(item)
                    t.setItem(i, 2, item)

                    color = p.get_color()
#                    if color is None:
#                        color = t.palette().color(t.backgroundRole())
                    if color is not None:
                        for item in items:
                            item.setBackground(color)

            t.resizeColumnsToContents()
        finally:
            self.__flag_updating_table = False

    def __lock_get_current_props(self):
        with self.__lock_propss:
            if len(self.__propss) > 0:
                return self.__propss[self.tableWidget.currentRow()]
            return None

    def __lock_get_current_propss(self):
        with self.__lock_propss:
            ii = self.tableWidget.selectedIndexes()
            i_rows = {idx.row() for idx in ii}
            propss = [self.__propss[i_row] for i_row in i_rows]
            return propss

    def __lock_check_dir_contents_changed(self):
        with self.__lock_propss:
            tw = self.tableWidget
            ir = tw.currentRow()
            ic = tw.currentColumn()

            flag_refresh = False
            filepaths = [p.filepath for p in self.__propss]

            for p in reversed(self.__propss):
                try:
                    t = os.path.getmtime(p.filepath)

                    if t != p.mtime:
                        # File has been changed, mark it as non scanned
                        p.flag_scanned = False
                        p.mtime = t
                        flag_refresh = True
                except OSError as E:
                    if E.errno == 2:
                        # File no longer exists
                        if p.row_index <= ir:
                            ir -= 1
                        self.__propss.remove(p)
                        flag_refresh = True
                    else:
                        raise

            # Newly created files will be added at the bottom and without any sorting
            for filepath in glob.glob(os.path.join(self.dir, "*")):
                if os.path.isfile(filepath):
                    if not filepath in filepaths:
                        p = _FileProps()
                        p.isfile = os.path.isfile(filepath)
                        p.filepath = filepath
                        p.mtime = os.path.getmtime(filepath)
                        self.__propss.append(p)
                        flag_refresh = True

        if flag_refresh:
            self.__lock_update_table()
            self.__update_info()
            if ir < tw.rowCount():
                # Tries to re-position cursor at cell
                tw.setCurrentCell(ir, ic)

    def __lock_set_dir(self, dir_):
        with self.__lock_propss:
            self.dir = os.path.relpath(dir_)
            self.__propss = []

            all_ = glob.glob(os.path.join(self.dir, "*"))
            dirs = list(filter(os.path.isdir, all_))
            dirs.sort()
            files = list(filter(os.path.isfile, all_))
            files.sort()
            dir_ = [os.path.join(self.dir, "..")] + dirs + files

            for i, f in enumerate(dir_):
                filepath = f  # os.path.join(self.dir, f)
                p = _FileProps()
                p.isfile = os.path.isfile(filepath)
                p.filepath = filepath
                p.mtime = os.path.getmtime(filepath)
                self.__propss.append(p)

    def __lock_auto_load(self):
        dir_ = glob.glob(os.path.join(self.dir, "*"))
#        dir_ = [x for x in dir_ if os.path.isfile(x)]
        sizes = [os.path.getsize(x) for x in dir_ if os.path.isfile(x)]
        sizes.sort()
        acc = np.cumsum(sizes)
        threshold = self.__get_auto_size()
        ww = np.where(acc <= threshold)
        if len(ww[0]) == 0:
            return
        max_size = min(sizes[ww[0][-1]], MAX_FILESIZE_AUTO_LOAD)
        # np.savetxt("brinca", sizes)
        # total = sum(sizes)
        # percentile = threshold/total
        #max_size = np.percentile(sizes, percentile)*100
        a99.get_python_logger().info("AUTO LOAD: max file size: {0:g}".format(max_size))
        propss = []
        with self.__lock_propss:
            for p in self.__propss:
                if p.isfile and os.path.getsize(p.filepath) <= max_size:
                    propss.append(p)

        # **Note** this was once crashing because Python modules were being imported
        # without filetype check. FilePy was implemented to be a base class for all
        # ".py-based" file types
        if len(propss) > 0:
            self.__set_status_text("Loading all files sized <= {0:g} kB...".format((max_size/1024)))
            self.__flag_loading = True
            t = self.__load_thread = LoadThread(self, propss)
            t.finished.connect(self.__finished_loading, Qt.QueuedConnection)
            t.start()

    def __lock_load(self, cls=None):
        propss = self.__lock_get_current_propss()
        if len(propss) > 0:
            with self.__lock_propss:
                self.__flag_loading = True
                self.__set_status_text("Loading file(s), please wait...")
                t = self.__load_thread = LoadThread(self, propss, cls)
                t.finished.connect(self.__finished_loading)
                t.start()

#
