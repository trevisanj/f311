__all__ = ["XPlotXYZ"]


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import a99
import f311.filetypes as ft


class XPlotXYZ(a99.XLogMainWindow):
    """
    Plots two fields of a SpectrumCollection object in a simple x-y plot

    Args:
      collection: SpectrumCollection object
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
        laa = keep_ref(QLabel("&Z-axis"))
        lwset.addWidget(laa)
        ###
        cbz = self.comboBoxZ = QComboBox()
        cbz.addItems(collection.fieldnames)
        laa.setBuddy(cbz)
        lwset.addWidget(cbz)
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
            ax = fig.gca(projection='3d')

            fieldname_x = str(self.comboBoxX.currentText())
            fieldname_y = str(self.comboBoxY.currentText())
            fieldname_z = str(self.comboBoxZ.currentText())

            spectra = self.collection.spectra
            n = len(spectra)
            xx, yy, zz = np.zeros((n,)), np.zeros((n,)), np.zeros((n,))
            for i, sp in enumerate(spectra):
                s_x = sp.more_headers.get(fieldname_x)
                s_y = sp.more_headers.get(fieldname_y)
                s_z = sp.more_headers.get(fieldname_z)

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
                try:
                    zz[i] = float(s_z)
                except TypeError:
                    pass

            # 3D plot will be a scatter plot, no need to sort; besides, should we sort using X or Y?
            #
            # sort_idxs = np.argsort(xx)
            # xx = xx[sort_idxs]
            # yy = yy[sort_idxs]
            # zz = zz[sort_idxs]

            ax.plot3D(xx, yy, zz, 'ok', lw=2)
            plt.xlabel(fieldname_x)
            plt.ylabel(fieldname_y)
            plt.ylabel(fieldname_z)
            a99.format_BLB()
            self.canvas.draw()

        except Exception as e:
            self.add_log_error("Could draw figure: "+a99.str_exc(e), True)
