__all__ = ["XPlotXY"]


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import matplotlib.pyplot as plt
import a99
import f311.filetypes as ft


LINE_COLOR = 'k'
LINE_WIDTH = 2


class XPlotXY(a99.XLogMainWindow):
    """
    Plots two fields of a SpectrumCollection object in a simple x-y plot

    Args:
      collection: SpectrumCollection object
    """
    def __init__(self, collection, *args):
        a99.XLogMainWindow.__init__(self, *args)

        self._refs = []
        self._drawers = [self._draw_line, self._draw_error]
        self._buttons = []
        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        assert isinstance(collection, ft.SpectrumCollection)
        self.collection = collection

        lw1 = keep_ref(QVBoxLayout())


        # First bar of plot options

        lwset0 = keep_ref(QHBoxLayout())
        lw1.addLayout(lwset0)
        ## Radio buttons for plot type
        # Radio button group probably needs its own layout, I think
        lwset0.addWidget(keep_ref(QLabel("Plot type")))
        lwset01 = QHBoxLayout()
        lwset0.addLayout(lwset01)
        r = self.rb_line = QRadioButton("Line")
        r.setChecked(True)
        self._buttons.append(r)
        lwset01.addWidget(r)
        r = self.rb_error = QRadioButton("Error bars")
        r.setToolTip("Groupx points by x-value and plots error bars "
                     "(center: mean; bar: +- standard deviation")
        self._buttons.append(r)
        lwset01.addWidget(r)
        lwset0.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Second bar of plot options

        lwset1 = keep_ref(QHBoxLayout())
        lw1.addLayout(lwset1)
        ###
        laa = keep_ref(QLabel("&X-axis"))
        lwset1.addWidget(laa)
        ###
        cbx = self.comboBoxX = QComboBox()
        cbx.addItems(collection.fieldnames)
        laa.setBuddy(cbx)
        lwset1.addWidget(cbx)
        ###
        laa = keep_ref(QLabel("&Y-axis"))
        lwset1.addWidget(laa)
        ###
        cby = self.comboBoxY = QComboBox()
        cby.addItems(collection.fieldnames)
        laa.setBuddy(cby)
        lwset1.addWidget(cby)
        ###
        b = keep_ref(QPushButton("Re&draw"))
        lwset1.addWidget(b)
        b.clicked.connect(self.redraw)
        ###
        lwset1.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))


        ###
        wm = keep_ref(QWidget())
        # a99.set_margin(wm, 0)
        lw1.addWidget(wm)
        self.figure, self.canvas, self.lfig = a99.get_matplotlib_layout(wm)

        cw = self.centralWidget = QWidget()
        cw.setLayout(lw1)
        self.setCentralWidget(cw)
        self.setWindowTitle("Plot Two Spectrum Collection Fields as a X-Y Chart")

        # self.redraw()

    # def get_redshift(self):
    #     return float(self.spinBox_redshift.value())


    # def spinBoxValueChanged(self, *args):
    #     self.label_redshiftValue.setText(str(self.get_redshift()))


    def redraw(self):
        try:
            idx = self._get_plot_type_index()
            if idx == -1:
                raise RuntimeError("Cannot draw, plot type not selected")

            fig = self.figure
            fig.clear()

            fieldname_x = str(self.comboBoxX.currentText())
            fieldname_y = str(self.comboBoxY.currentText())

            spectra = self.collection.spectra
            n = len(spectra)
            xx = np.zeros((n,))
            yy = np.zeros((n,))
            for i, sp in enumerate(spectra):
                s_x = sp.more_headers.get(fieldname_x)
                s_y = sp.more_headers.get(fieldname_y)

                # Will ignore error converting to float
                # Cells giving error will be zero
                try:
                    xx[i] = float(s_x)
                except TypeError:
                    pass
                try:
                    yy[i] = float(s_y)
                except TypeError:
                    pass

            sort_idxs = np.argsort(xx)

            xx = xx[sort_idxs]
            yy = yy[sort_idxs]

            self._drawers[idx](xx, yy)

            # Final adjustments
            k = 0.02 # percentual margin to the left and to the right
            xmin, xmax = np.min(xx), np.max(xx)
            xspan = xmax-xmin
            margin = .5 if xspan == 0 else xspan*k
            plt.xlim([xmin-margin, xmax+margin])
            plt.xlabel(fieldname_x)
            plt.ylabel(fieldname_y)
            plt.setp(list(plt.gca().spines.values()), linewidth=2)

            a99.format_BLB()
            self.canvas.draw()

        except Exception as e:
            a99.get_python_logger().exception("Error plotting")
            self.add_log_error("Could draw figure: "+a99.str_exc(e), True)


    def _get_plot_type_index(self):
        for i, b in enumerate(self._buttons):
            if b.isChecked():
                return i
        return -1


    def _draw_line(self, xx, yy):
        plt.plot(xx, yy, lw=2, color=LINE_COLOR)

    def _draw_error(self, xx, yy):
        """Draws error plot using x-values to group y-values"""

        xunique = np.unique(xx)
        n = len(xunique)
        y, errors = np.zeros(n), np.zeros(n)

        for i, xnow in enumerate(xunique):
            ysel = yy[xx == xnow]
            y[i] = np.mean(ysel)
            errors[i] = np.std(ysel)

        plt.plot(xunique, y, color=LINE_COLOR, lw=LINE_WIDTH, linestyle="--")
        plt.errorbar(xunique, y, yerr=errors, fmt="o", markeredgewidth=LINE_WIDTH, markersize=8, markerfacecolor=(1., 1., 1.), color=LINE_COLOR, lw=LINE_WIDTH)
