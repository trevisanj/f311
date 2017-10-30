"""Widget to edit a series of points on top of a spectrum"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import a99
import matplotlib.pyplot as plt
import copy

__all__ = ["WContinua"]

_COLOR_LINE = (.91, .13, 0)
_COLOR_MARKER = (.92, .132, 0)
_COLOR_SPECTRUM = (0., .2, .9)
_LINESTYLE_CONTINUUM = "solid"
_LINESTYLE_SPECTRUM = "dashed"
_LINEWIDTH = 1
_MARKER = "s"


class WContinua(a99.WConfigEditor):

    @property
    def continua(self):
        return self._continua

    @continua.setter
    def continua(self, value):
        self._continua = value if value is not None else []

    @property
    def spectrum(self):
        return self._spectrum

    @spectrum.setter
    def spectrum(self, value):
        self._spectrum = value
        self._update_self()
        self._draw()

    def __init__(self, parent_form):
        a99.WConfigEditor.__init__(self, parent_form)

        self._spectrum = None
        # matplotlib plot corresponding to self._spectrum
        self._plot_sp = None
        self._draw_last_name = "!&*@*@*#@#*@#"  # improbable name
        self._continua = []

        lw0 = self.layout_main = QVBoxLayout()
        self.setLayout(lw0)

        sp = self.splitter = QSplitter(Qt.Horizontal)
        self.layout_editor.addWidget(sp)

        wsp = a99.keep_ref(QWidget())
        sp.addWidget(wsp)
        ly_wsp = QVBoxLayout(wsp)

        toolbar0 = self._get_toolbar0()
        ly_wsp.addWidget(toolbar0)

        a = self.tableWidget = self._get_tableWidget0()
        ly_wsp.addWidget(a)

        # Matplotlib area

        wm = a99.keep_ref(QWidget())
        # a99.set_margin(wm, 0)
        sp.addWidget(wm)
        self.figure, self.canvas, self.lfig = a99.get_matplotlib_layout(wm)
        self.canvas.mpl_connect('button_press_event', self._on_plot_click)

        # name, property
        self._map = [
            a99.CEMapItem("continua", self),
        ]

    # GUI artists

    def _get_toolbar0(self):
        # ## Actions
        action = self.action_insert = QAction(a99.get_icon("list-add"), "&Insert...", self)
        action.triggered.connect(self.on_insert)
        action.setShortcut("Ins")

        action = self.action_edit = QAction(a99.get_icon("gtk-edit"), "&Edit...", self)
        action.triggered.connect(self.on_edit)
        action.setShortcut("Enter")

        action = self.action_delete = QAction(a99.get_icon("trash"), "&Delete", self)
        action.setShortcut("Del")
        action.triggered.connect(self.on_delete)

        # Adds actions to toolbar

        tb = QToolBar()
        tb.setOrientation(Qt.Horizontal)
        tb.addAction(self.action_insert)
        tb.addAction(self.action_edit)
        tb.addAction(self.action_delete)

        return tb

    def _get_tableWidget0(self):
        a = QTableWidget()
        a.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        a.setSelectionMode(QAbstractItemView.SingleSelection)
        a.setSelectionBehavior(QAbstractItemView.SelectRows)
        a.setAlternatingRowColors(True)
        a.setEditTriggers(QAbstractItemView.NoEditTriggers)
        a.setFont(a99.MONO_FONT)
        # a.installEventFilter(self)
        # a.setContextMenuPolicy(Qt.CustomContextMenu)
        # a.customContextMenuRequested.connect(self.on_twSpectra_customContextMenuRequested)
        # a.setSortingEnabled(True)
        # a.cellChanged.connect(self.on_twSpectra_cellChanged)
        a.itemSelectionChanged.connect(self._on_tableWidget_itemSelectionChanged)
        return a

    # WConfigEditor override

    def _after_update_gui(self):
        self._populate()
        self._draw()

    def _after_update_fobj(self):
        newcontinua = [copy.copy(continuum) for continuum in self._f.obj["continua"]]
        for continuum in newcontinua:
            continuum["plot0"] = None
            continuum["plot1"] = None

        self._f.obj["continua"] = newcontinua

    # Slots

    def _on_plot_click(self, event):
        print('{} click: button={}, x={}, y={}, xdata={}, ydata={}'.format(
              'double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))

        x, y = event.xdata, event.ydata

        if x is None:
            return

        sp = self.spectrum
        if sp is not None:
            idx = a99.index_nearest(sp.x, x)
            print("Lambda is actually {}".format(sp.x[idx]))

        if event.button == 1:
            self._insert_point(x, y)
        elif event.button == 3:
            self._delete_nearest(x, y)

    def _on_tableWidget_itemSelectionChanged(self):
        self._update_fobj()
        self._draw()
        self.changed.emit()

    def _sth_changed(self):
        self._update_fobj()
        self.changed.emit()

    def on_insert(self):
        if self._do_on_insert():
            self._update_fobj()
            self.changed.emit()

    def on_edit(self):
        if self._get_continuum_index() is None:
            return
        if self._do_on_edit():
            self._update_fobj()
            self.changed.emit()

    def on_delete(self):
        if self._get_continuum_index() is None:
            return
        if self._do_on_delete():
            self._update_fobj()
            self.changed.emit()

    # Internal

    def _get_new_continuum(self, name):
        return {"name": name, "points": [], "plot0": None, "plot1": None}

    def _get_continuum_index(self):
        """Returns index of selected continuum"""
        n = len(self._continua)
        if n == 0:
            return None
        index = self.tableWidget.currentRow()
        if index > len(self._continua)-1:
            return None
        return index

    def _get_continuum(self):
        """Returns selected continuum"""
        index = self._get_continuum_index()
        if index is None:
            return None
        return self._continua[index]

    def _get_continuum_name(self):
        """Returns selected continuum"""
        cuum = self._get_continuum()
        return None if cuum is None else cuum["name"]

    def _get_points(self):
        return self._get_continuum()["points"]

    def _do_on_insert(self):
        name = a99.random_name()
        while True:
            params = a99.Parameters({"name": name})
            form = a99.XParametersEditor(specs=params, title="Insert continuum")
            r = form.exec_()
            if not (r == QDialog.Accepted):
                return

            name = form.get_kwargs()["name"]
            if self._find_continuum_name(name) is not None:
                a99.show_error("Name already exists")
                continue

            self._continua.append(self._get_new_continuum(name))
            continuum = self._get_continuum()
            self._populate()
            if continuum is not None:
                self._position_at_name(continuum["name"])

            return True

    def _do_on_edit(self):
        continuum = self._get_continuum()
        name = continuum["name"]
        while True:
            r, form = a99.show_edit_form({"name": name}, None, "Edit continuum name")
            if not (r == QDialog.Accepted):
                return

            newname = form.get_kwargs()["name"]
            if any([cuum_["name"] == newname for cuum_ in self._continua if cuum_ != continuum]):
                a99.show_error("Name already exists")
                continue

            continuum["name"] = newname
            self.tableWidget.item(self._get_continuum_index(), 0).setText(newname)

            return True

    def _do_on_delete(self):
        r = QMessageBox.question(None, "Delete continuum",
                                 "Are you sure?",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r == QMessageBox.Yes:
            index = self._get_continuum_index()
            del self._continua[index]
            self._populate()
            if index <= len(self._continua):
                self.tableWidget.setCurrentCell(index, 0)

            return True


    def _position_at_name(self, name):
        """Positions table widget at continuum given by name"""
        a = self.tableWidget
        idx = self._find_continuum_name(name)
        save = a.blockSignals(True)
        a.setCurrentCell(idx, 0)
        a.blockSignals(save)

    def _find_continuum_name(self, name):
        """Returns index of continuum or None"""
        a = self.tableWidget
        for i in range(a.rowCount()):
            if a.item(i, 0).text() == name:
                return i
        return None

    def _update_self(self):
        """Changes to internal state sensible to current internal state"""






# TODO Auto make continuum to start with
        # sp = self._spectrum
        # if self._points is None and sp is not None:
        #     if False:
        #         y0, y1 = sp.y[0], sp.y[-1]
        #     else:
        #         y0, y1 = 1., 1.
        #     self._points = [(sp.l0, y0), (sp.lf, y1)]


    def _lose_plots(self):

        for cuum in self._continua:
            cuum["plot0"] = None
            cuum["plot1"] = None
        self._plot_sp = None

    def _draw(self):
        import f311.explorer as ex

        def _ensure_new_fig():
            fig = self.figure
            fig.clear()
            plt.figure(fig.number)
            while True:
                yield
        enfig = _ensure_new_fig()

        try:
            a99.format_BLB()

            name = self._get_continuum_name()
            if name != self._draw_last_name:
                self._lose_plots()
                next(enfig)
            self._draw_last_name = name


            # Spectrum
            sp = self._spectrum
            if sp is not None:
                ######################### next(enfig)
                if self._plot_sp is None:
                    self._plot_sp, = plt.plot(sp.x, sp.y, label=str(sp.title), color=_COLOR_SPECTRUM,
                             linestyle=_LINESTYLE_SPECTRUM, linewidth=_LINEWIDTH)
                    setup = ex.PlotSpectrumSetup()
                    plt.xlabel(setup.fmt_xlabel.format(sp))
                else:
                    print("SSSSSSSSSSSSSSSSSSSSSSS", self._plot_sp)
                    self._update_plot_data(self._plot_sp, zip(sp.x, sp.y))

                xmin, xmax, ymin, ymax, xspan, yspan = ex.calc_max_min([sp])
                ymin, ymax = min(0., ymin), max(1., ymax)

                _T = 0.02  # fraction of extra space on left, right, top, bottom of graphics
                plt.xlim([xmin - xspan * _T, xmax + xspan * _T])
                plt.ylim([ymin - yspan * _T, ymax + yspan * _T])


            # Continua
            cuum = self._get_continuum()
            if cuum is not None:
                points = cuum["points"]

                p0 = cuum["plot0"]
                if p0:
                    self._update_plot_data(p0, points)
                    self._update_plot_data(cuum["plot1"], points)
                else:
                    xx, yy = self._get_xx_yy(points)
                    ########################################## next(enfig)
                    cuum["plot0"], = plt.plot(xx, yy, c=_COLOR_LINE, linestyle=_LINESTYLE_CONTINUUM,
                         linewidth=_LINEWIDTH)
                    cuum["plot1"], = plt.plot(xx, yy, c=_COLOR_MARKER, linestyle="None", marker=_MARKER)

            try:
                self.figure.tight_layout()
            except:
                a99.get_python_logger().exception("WContinua._draw()")

        except:
            a99.get_python_logger().exception("WContinua._draw()")
        finally:
            self.canvas.draw()

    def _update_plot_data(self, plot, points):
        xx, yy = self._get_xx_yy(points)
        plot.set_xdata(xx)
        plot.set_ydata(yy)

    def _get_xx_yy(self, points):
        try:
            xx, yy = zip(*points)
        except (ValueError, TypeError):
            xx, yy = [], []
        return xx, yy

    def _insert_point(self, x, y):
        cuum = self._get_continuum()
        if cuum is None:
            return
        pp = cuum["points"]
        p = (x, y)
        idx = -1
        if len(pp) > 0:
            xx, _ = zip(*pp)
            idx = a99.BSearchCeil(xx, x)
        if idx == -1:
            pp.append(p)
        else:
            pp.insert(idx, p)

        self._draw()
        self.changed.emit()

    def _delete_nearest(self, x, y):
        """Deletes point nearest to (x, y) (actually ignores the y)"""

        cuum = self._get_continuum()
        if cuum is None:
            return
        pp = cuum["points"]

        if len(pp) == 0:
            return

        xx, _ = zip(*pp)
        index = a99.index_nearest(xx, x)
        del pp[index]

        self._draw()
        self.changed.emit()

    def _populate(self):
        _HEADERS = ["Name"]

        cc = self._continua
        nr, nc = len(cc), len(_HEADERS)
        t = self.tableWidget
        a99.reset_table_widget(t, nr, nc)
        t.setHorizontalHeaderLabels(_HEADERS)
        i_row = 0
        for i, continuum in enumerate(cc):
            item = QTableWidgetItem(continuum["name"])
            t.setItem(i_row, 0, item)

            i_row += 1

        t.resizeColumnsToContents()
