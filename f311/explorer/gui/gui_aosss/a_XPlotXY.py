__all__ = ["XPlotXY"]


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import matplotlib.pyplot as plt
import a99
from .... import explorer as ex
import f311.filetypes as ft


class XPlotXY(a99.XLogMainWindow):
    """
    Plots two fields of a SpectrumCollection object in a simple x-y plot

    Arguments:
      collection -- SpectrumCollection object
    """
    def __init__(self, collection, *args):
        a99.XLogMainWindow.__init__(self, *args)

        self._refs = []
        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        assert isinstance(collection, ft.SpectrumCollection)
        self.collection = collection

        lw1 = keep_ref(QVBoxLayout())

        lwset = keep_ref(QHBoxLayout())
        lw1.addLayout(lwset)
        ###
        laa = keep_ref(QLabel("&X-axis"))
        lwset.addWidget(laa)
        ###
        cbx = self.comboBoxX = QComboBox()
        cbx.addItems(collection.fieldnames)
        laa.setBuddy(cbx)
        lwset.addWidget(cbx)
        ###
        laa = keep_ref(QLabel("&Y-axis"))
        lwset.addWidget(laa)
        ###
        cby = self.comboBoxY = QComboBox()
        cby.addItems(collection.fieldnames)
        laa.setBuddy(cby)
        lwset.addWidget(cby)
        ###
        b = keep_ref(QPushButton("Re&draw"))
        lwset.addWidget(b)
        b.clicked.connect(self.redraw)
        ###
        lwset.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))


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

            plt.plot(xx, yy, lw=2, color='k')
            plt.xlabel(fieldname_x)
            plt.ylabel(fieldname_y)
            a99.format_BLB()
            self.canvas.draw()

        except Exception as e:
            self.add_log_error("Could draw figure: "+a99.str_exc(e), True)
