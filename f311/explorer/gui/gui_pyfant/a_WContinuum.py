"""Widget to edit a series of points on top of a spectrum"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import a99
import matplotlib.pyplot as plt

__all__ = ["WContinuum"]

_COLOR_LINE = (.91, .13, 0)
_COLOR_MARKER = (.92, .132, 0)
_COLOR_SPECTRUM = (0., .2, .9)
_LINESTYLE_CONTINUUM = "solid"
_LINESTYLE_SPECTRUM = "dashed"
_LINEWIDTH = 1
_MARKER = "s"


class WContinuum(a99.WBase):

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        self._points = value
        self._update_self()
        self._update_gui()

    @property
    def spectrum(self):
        return self._spectrum

    @spectrum.setter
    def spectrum(self, value):
        self._spectrum = value
        self._update_self()
        self._update_gui()

    def __init__(self, parent_form, spectrum=None, points=None):
        a99.WBase.__init__(self, parent_form)

        self._spectrum = spectrum
        self._points = points

        lw0 = self.layout_main = QVBoxLayout()
        self.setLayout(lw0)

        # Toolbar

        lwtb = self.keep_ref(QHBoxLayout())
        lw0.addLayout(lwtb)
        ###
        laa = self.label_llzero = QLabel("No tools yet")
        lwtb.addWidget(laa)
        ###
        lwtb.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Matplotlib area

        wm = a99.keep_ref(QWidget())
        # a99.set_margin(wm, 0)
        lw0.addWidget(wm)
        self.figure, self.canvas, self.lfig = a99.get_matplotlib_layout(wm)
        self.canvas.mpl_connect('button_press_event', self._on_plot_click)

        self._update_self()
        self._update_gui()

    def _sth_changed(self):
        self._update_fobj()
        self.changed.emit()

    def _update_self(self):
        """Changes to internal state sensible to current internal state"""
        sp = self._spectrum
        if self._points is None and sp is not None:
            if False:
                y0, y1 = sp.y[0], sp.y[-1]
            else:
                y0, y1 = 1., 1.
            self._points = [(sp.l0, y0), (sp.lf, y1)]

    def _update_gui(self):
        """Changes to GUI sensible to internal state"""
        self._draw()

    def _draw(self):
        import f311.explorer as ex

        fig = self.figure
        fig.clear()
        plt.figure(fig.number)

        try:
            a99.format_BLB()

            # Spectrum
            sp = self._spectrum
            if sp is not None:
                setup = ex.PlotSpectrumSetup()
                plt.plot(sp.x, sp.y, label=str(sp.title), color=_COLOR_SPECTRUM,
                         linestyle=_LINESTYLE_SPECTRUM, linewidth=_LINEWIDTH)
                plt.xlabel(setup.fmt_xlabel.format(sp))

                xmin, xmax, ymin, ymax, xspan, yspan = ex.calc_max_min([sp])
                ymin, ymax = min(0., ymin), max(1., ymax)

                _T = 0.02  # fraction of extra space on left, right, top, bottom of graphics
                plt.xlim([xmin - xspan * _T, xmax + xspan * _T])
                plt.ylim([ymin - yspan * _T, ymax + yspan * _T])


            # Continuum
            if self._points is not None:
                xx, yy = zip(*self._points)
                plt.plot(xx, yy, c=_COLOR_LINE, linestyle=_LINESTYLE_CONTINUUM, linewidth=_LINEWIDTH)

                plt.plot(xx, yy, c=_COLOR_MARKER, linestyle="None", marker=_MARKER)

            try:
                fig.tight_layout()
            except:
                a99.get_python_logger().exception("WContinuum._draw()")

        except:
            a99.get_python_logger().exception("WContinuum._draw()")
        finally:
            self.canvas.draw()


    def _on_plot_click(self, event):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))

        x, y = event.xdata, event.ydata
        sp = self.spectrum
        print("XXXXXXXXX {} YYYYYYYYYY {}".format(x, y))

        if sp is not None:

            idx = a99.index_nearest(sp.x, x)
            print("Lambda is actually {}".format(sp.x[idx]))

        if event.button == 1:
            self._insert_point(x, y)
        elif event.button == 3:
            self._delete_nearest(x, y)

    def _insert_point(self, x, y):
        p = (x, y)
        pp = self._points
        xx, _ = zip(*pp)
        idx = a99.BSearchCeil(xx, x)
        if idx == -1:
            pp.append(p)
        else:
            pp.insert(idx, p)
        self._update_gui()

    def _delete_nearest(self, x, y):
        """Deletes point nearest to (x, y) (actually ignores the y)"""

        sp = self._spectrum
        if sp is not None:
            pp = self._points

            if len(pp) < 3:
                self.add_log_error("Need at least two points")
                return

            xx, _ = zip(*pp)
            index = a99.index_nearest(xx, x)
            del pp[index]

            self._update_gui()
