#!/usr/bin/env python


"""
Draws chart showing spectral lines of interest, spectrograph wavelength ranges, ESO atmospheric model, etc.

Two modes are available:
  - GUI mode (default): opens a GUI allowing for setup parameters
  - Plot mode (--plot): plots the chart directly in default way
"""


import sys
import argparse
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib as mpl
import numpy as np
import numbers
from PyQt5.QtWidgets import *
import logging
from f311 import aosss as ao
from f311 import physics as ph
import a99


a99.logging_level = logging.INFO
a99.flag_log_file = True



###############################################################################
# # External setup
mpl.rcParams['axes.linewidth'] = 2


###############################################################################
# # local class & function library
class MyLine(object):
    def __init__(self, name, wl, width=0, position=0, reference=None):
        self.name = name
        self.wl = wl if isinstance(wl, (list, tuple)) else [wl]
        self.width = width
        self.reference = reference  # paper etc
        if width > 0 and not isinstance(wl, numbers.Number):
            raise RuntimeError("Either specify list of lines or width")
        self.position = position

def lambda_shift(lambda_0, v_radial):
    """Calculates delta_lambda due to Doppler effect given emitter wavelength and radial velocity in km/s.
    Positive radial velocity means running away from us."""
    C = 300000  # light speed in km/s
    return lambda_0*(C+v_radial)/C

class MyCoverage(object):
    """Stores data for the wavelength coverage of a certain instrument/mode etc"""
    def __init__(self, name, l0lf):
        self.name = name
        self.l0lf = l0lf  # sequence of tuples

###############################################################################
# # Data definition
NUM_SLOTS = 10
LAST_BAND = "K"
COLOR_COVERAGE = np.array([.5, .5, .5])
COLOR_GRID = np.array((.5, .5, .5))
COLOR_BAND = [0., .3, 0.]
COLOR_SPECTRUM = [.2, .2, .2]
COLOR_TELLURIC_BOX = [182./255, 234./255, 232./255]
COLOR_TEXT = (.25, .2, .2)

HA_LAMBDA = 6562.8
HA_WIDTH = lambda_shift(HA_LAMBDA, 400) - lambda_shift(HA_LAMBDA, -400)

ll = [MyLine("CaHK", 3900),
      MyLine("Sr", 4050),
      MyLine("C", 4300),
      MyLine("Mgb", [5167.32, 5172.68, 5183.6]),
      MyLine("NaD", [5889.95, 5895.92]),
      MyLine("CaI", 6162),
      MyLine(r"H$\alpha$", 6562.8, width=HA_WIDTH),
      MyLine("OI triplet", [7777.194, 7777.417, 7777.539]),
      MyLine("CaII triplet", [8498, 8542, 8662]),
      MyLine("He II", [1640]),
      MyLine("Lyman limit", 912.),
      MyLine("O II", 3727, reference="MPuech 2008"),
      MyLine("OH", 3064, reference="Castilho (Thesis) 1999"),
      MyLine("Be", 3131, reference="Castilho (Thesis) 1999"),
      MyLine("NH", 3360, reference="Castilho (Thesis) 1999"),
      MyLine("FeI, TiI, SiI, MgI", [11896, 11953, 11988, 11995, 12035, 12107, 11831, 12087, 11597, 11611, 11641, 11693, 11783, 11887, 11976], reference="Cevans 2011"),  # apud Davies et. al (2010)
      # MyLine("FeI", 11887, reference="Davies et. al (2010)"),
      # MyLine("FeI", 11641, reference="Davies et. al (2010)"),
      # MyLine("FeI", 11611, reference="Davies et. al (2010)"),
      # MyLine("MgI", 12087, reference="Davies et. al (2010)"),
      # MyLine("MgI", 11831, reference="Davies et. al (2010)"),
      # MyLine("MgI", 11831, reference="Davies et. al (2010)"),
      ]

cc = [MyCoverage("HMM", [(4000, 18000)]),
      MyCoverage("HDM (essential)", [(10000, 18000)]),
      MyCoverage("HDM (desirable)", [(8000, 25000)]),
      MyCoverage("IGM (essential)", [(4000, 8000)]),
      MyCoverage("IGM (desirable)", [(3700, 10000)])
      ]


# ###############################################################################
# def draw(fig, telluric_spectra, redshift=0):
#     l0, lf = 3000, a99.get_ubv_bandpass("K").lf
#     x =  np.logspace(np.log10(l0), np.log10(lf), 1000, base=10.)
#
#     ax = fig.gca()
#     ax.set_axisbelow(True)
#
#     # # grid
#     #   ====
#     # http://matplotlib.org/examples/pylab_examples/major_minor_demo1.html
#     majorLocator_x = MultipleLocator(1000)
#     majorFormatter_x = FormatStrFormatter('%d')
#     minorLocator_x = MultipleLocator(250)
#     ax.xaxis.set_major_locator(majorLocator_x)
#     ax.xaxis.set_major_formatter(majorFormatter_x)
#     # for the minor ticks, use no labels; default NullFormatter
#     ax.xaxis.set_minor_locator(minorLocator_x)
#
#     majorLocator_y = MultipleLocator(1.)
#     majorFormatter_y = FormatStrFormatter('')
#     # minorLocator_x = MultipleLocator(250)
#     ax.yaxis.set_major_locator(majorLocator_y)
#     ax.yaxis.set_major_formatter(majorFormatter_y)
#     # for the minor ticks, use no labels; default NullFormatter
#     # ax.xaxis.set_minor_locator(minorLocator_x)
#
#     g0 = plt.grid(True, which='major', axis='x', linewidth=2, linestyle=':', color=COLOR_GRID)
#     plt.grid(True, which='major', axis='y', linewidth=1, linestyle='-', color=COLOR_GRID*1.5)
#     plt.grid(True, which='minor', axis='x', linestyle=':', color=COLOR_GRID)
#
#
#     # # bands
#     #   =====
#     for band_name, bandpass in ph.get_ubv_bandpasses_dict().items():
#         y = bandpass.ufunc()(x)*.75
#         plt.plot(x, y, label=band_name, c=COLOR_BAND)
#         idx_max = np.argmax(y)
#         ax.annotate(band_name, xy=(x[idx_max], y[idx_max]+.1),
#                     horizontalalignment="center", verticalalignment="center",
#                     color=COLOR_TEXT)
#
#         if band_name == LAST_BAND:
#             break
#
#     # # Telluric features
#     Y_TOP = 2
#     Y_BOTTOM = Y_TOP-1+0.01
#     SPECTRUM_HEIGHT = 0.9  # Height for the spectrum to span in the chart
#     ax.annotate("Telluric features", xy=[l0, Y_TOP-.02], color=COLOR_TEXT, verticalalignment="top")
#     for sp in telluric_spectra:
#         # let ymin=0 (maybe there is no zero transmission in the spectrum,
#         # it will be good to see that frequencies are not completely attenuated)
#         ymax, ymin = max(sp.y), 0
#         x0, x1, y0, y1 = sp.x[0], sp.x[-1], Y_BOTTOM, Y_BOTTOM+SPECTRUM_HEIGHT
#         ax.fill_between([x0, x1], [y1, y1], [y0, y0], color=COLOR_TELLURIC_BOX)
#         ax.plot(sp.x, (sp.y-ymin)*SPECTRUM_HEIGHT+Y_BOTTOM, c=COLOR_SPECTRUM)
#
#
#     # # Chemical lines of interest (redshifted or not)
#     Y_TOP = NUM_SLOTS
#     COLOR_LINES = np.array([.3, 0., .3])
#     for line in ll:
#         wl = [x*(1+redshift) for x in line.wl]
#         if line.width > 0:
#             width = line.width*(1+redshift)
#             plt.fill_between([wl[0]-width/2, wl[0]+width/2],
#                              [Y_TOP, Y_TOP], [0, 0], color=COLOR_LINES, alpha=1)
#             x_ann = wl[0]+width/2
#         else:
#             for x in wl:
#                 plt.plot([x, x], [0, Y_TOP], c=COLOR_LINES, alpha=1)
#             x_ann = max(wl)
#         plt.annotate(line.name, xy=(x_ann, Y_TOP-.2), rotation=-90, color=COLOR_TEXT)
#
#
#     # # coverages
#     #   =========
#     HEIGHT = .7
#     y = NUM_SLOTS-(1-HEIGHT)/2-1
#     for coverage in cc:
#         for interval in coverage.l0lf:
#             x0, x1 = interval
#             plt.plot([x0, x1, x1, x0, x0], [y, y, y-HEIGHT, y-HEIGHT, y], color=COLOR_COVERAGE*.5, alpha=.8)
#             plt.fill_between(interval, [y, y], [y-HEIGHT, y-HEIGHT], color=COLOR_COVERAGE, alpha=.6, hatch='//')
#             x_ann = interval[1]
#         plt.annotate(coverage.name, xy=(x_ann+40, y-HEIGHT/2), color=COLOR_TEXT, verticalalignment="center")
#         y -= 1
#
#     plt.xlim([l0, lf])
#     plt.ylim([0, NUM_SLOTS+.01])
#     plt.xlabel("Wavelength ($\AA$)")
#     plt.tight_layout()
#


###############################################################################
def draw(fig, sp_sky, redshift=0):
    l0, lf = 3000, ph.get_ubv_bandpass("K").lf
    x =  np.logspace(np.log10(l0), np.log10(lf), 1000, base=10.)

    ax = fig.gca()
    ax.set_axisbelow(True)

    # # grid
    #   ====
    # http://matplotlib.org/examples/pylab_examples/major_minor_demo1.html
    majorLocator_x = MultipleLocator(1000)
    majorFormatter_x = FormatStrFormatter('%d')
    minorLocator_x = MultipleLocator(250)
    ax.xaxis.set_major_locator(majorLocator_x)
    ax.xaxis.set_major_formatter(majorFormatter_x)
    # for the minor ticks, use no labels; default NullFormatter
    ax.xaxis.set_minor_locator(minorLocator_x)

    majorLocator_y = MultipleLocator(1.)
    majorFormatter_y = FormatStrFormatter('')
    # minorLocator_x = MultipleLocator(250)
    ax.yaxis.set_major_locator(majorLocator_y)
    ax.yaxis.set_major_formatter(majorFormatter_y)
    # for the minor ticks, use no labels; default NullFormatter
    # ax.xaxis.set_minor_locator(minorLocator_x)

    g0 = plt.grid(True, which='major', axis='x', linewidth=2, linestyle=':', color=COLOR_GRID)
    plt.grid(True, which='major', axis='y', linewidth=1, linestyle='-', color=COLOR_GRID*1.5)
    plt.grid(True, which='minor', axis='x', linestyle=':', color=COLOR_GRID)


    # # bands
    #   =====
    for band_name, bandpass in ph.get_ubv_bandpasses_dict().items():
        y = bandpass.ufunc()(x)*.75
        plt.plot(x, y, label=band_name, c=COLOR_BAND)
        idx_max = np.argmax(y)
        ax.annotate(band_name, xy=(x[idx_max], y[idx_max]+.1),
                    horizontalalignment="center", verticalalignment="center",
                    color=COLOR_TEXT)

        if band_name == LAST_BAND:
            break

    # # ESO sky model
    if sp_sky:
        tt = ["Atmospheric emission", "Atmospheric transmission"]
        y_top = 3
        SPECTRUM_HEIGHT = 0.9  # Height for the spectrum to span in the chart
        for i, sp in enumerate(sp_sky):
            y_bottom = y_top-1+0.01
            # let ymin=0 (maybe there is no zero transmission in the spectrum,
            ymax, ymin = max(sp.y), 0
            y = sp.y/ymax
            x0, x1, y0, y1 = sp.x[0], sp.x[-1], y_bottom, y_bottom+SPECTRUM_HEIGHT
            ax.annotate(tt[i], xy=[l0, y_top-.42], color=COLOR_TEXT, verticalalignment="top")
            ax.fill_between([x0, x1], [y1, y1], [y0, y0], color=COLOR_TELLURIC_BOX)
            ax.plot(sp.x, (y-ymin)*SPECTRUM_HEIGHT+y_bottom, c=COLOR_SPECTRUM)

            y_top -= 1


    # # Chemical lines of interest (redshifted or not)
    Y_TOP = NUM_SLOTS
    COLOR_LINES = np.array([.3, 0., .3])
    for line in ll:
        wl = [x*(1+redshift) for x in line.wl]
        if line.width > 0:
            width = line.width*(1+redshift)
            plt.fill_between([wl[0]-width/2, wl[0]+width/2],
                             [Y_TOP, Y_TOP], [0, 0], color=COLOR_LINES, alpha=1)
            x_ann = wl[0]+width/2
        else:
            for x in wl:
                plt.plot([x, x], [0, Y_TOP], c=COLOR_LINES, alpha=1)
            x_ann = max(wl)
        plt.annotate(line.name, xy=(x_ann, Y_TOP-.2), rotation=-90, color=COLOR_TEXT)


    # # coverages
    #   =========
    HEIGHT = .7
    y = NUM_SLOTS-(1-HEIGHT)/2-1
    for coverage in cc:
        for interval in coverage.l0lf:
            x0, x1 = interval
            plt.plot([x0, x1, x1, x0, x0], [y, y, y-HEIGHT, y-HEIGHT, y], color=COLOR_COVERAGE*.5, alpha=.8)
            plt.fill_between(interval, [y, y], [y-HEIGHT, y-HEIGHT], color=COLOR_COVERAGE, alpha=.6, hatch='//')
            x_ann = interval[1]
        plt.annotate(coverage.name, xy=(x_ann+40, y-HEIGHT/2), color=COLOR_TEXT, verticalalignment="center")
        y -= 1

    plt.xlim([l0, lf])
    plt.ylim([0, NUM_SLOTS+.01])
    plt.xlabel("Wavelength ($\AA$)")
    plt.tight_layout()



class RedshiftWindow(QMainWindow):
    def __init__(self, sp_sky):
        QMainWindow.__init__(self)

        self._refs = []
        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        self.sp_sky = sp_sky

        lw1 = keep_ref(QVBoxLayout())

        lwset = keep_ref(QHBoxLayout())
        lw1.addLayout(lwset)
        ###
        laa = keep_ref(QLabel("&Redshift"))
        lwset.addWidget(laa)
        ###
        sbx = self.spinBox_redshift = QDoubleSpinBox()
        laa.setBuddy(sbx)
        sbx.setSingleStep(.01)
        sbx.setDecimals(2)
        sbx.setMinimum(-.5)
        sbx.setMaximum(17)
        # sbx.valueChanged.connect(self.spinBoxValueChanged)
        lwset.addWidget(sbx)
        ###
        b = keep_ref(QPushButton("Redra&w"))
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
        self.setWindowTitle("MOSAIC Wavelength Chart")

        self.redraw()

    def get_redshift(self):
        return float(self.spinBox_redshift.value())


    # def spinBoxValueChanged(self, *args):
    #     self.label_redshiftValue.setText(str(self.get_redshift()))


    def redraw(self):
        try:
            fig = self.figure
            fig.clear()
            draw(fig, self.sp_sky, self.get_redshift())
            self.canvas.draw()
        except Exception as E:
            a99.get_python_logger().exception("Could not draw figure")



if __name__ == "__main__":

    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
    )
    parser.add_argument('--plot', action='store_const',
                        const=True, default=False,
                        help='Plot mode (default is GUI mode)')
    args = parser.parse_args()

    sp_sky = None
    try:
        sp_sky = ao.load_eso_sky()
    except:
        a99.get_python_logger().exception("Failed to load ESO sky model")

    if args.plot:
        fig = plt.figure()
        # draw(fig, telluric_spectra)
        draw(fig, sp_sky)
        plt.show()
    else:
        app = a99.get_QApplication([])
        form = RedshiftWindow(sp_sky)  # telluric_spectra)
        form.show()
        sys.exit(app.exec_())
