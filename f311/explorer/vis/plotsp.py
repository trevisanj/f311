"""
API in functional form for plotting spectra

Routines also used by plot-spectra.py
"""

import matplotlib.pyplot as plt
import math
import matplotlib.backends.backend_pdf
from matplotlib import rc
import logging
import numpy as np
import a99
import f311.filetypes as ft

__all__ = ["plot_spectra_stacked", "plot_spectra_overlapped", "plot_spectra_pieces_pdf",
 "plot_spectra_pages_pdf", "draw_spectra_stacked", "PlotSpectrumSetup", "draw_spectra_overlapped",
 "calc_max_min"]


_T = 0.02  # percentual amount of extra space on left, right, top, bottom of graphics
_FAV_COLOR = 'k'  # "favourite color" for single-spectrum plots


# TODO draw_spectra_overlapped (maybe when I need it)


def _set_plot(callable_, fmt, spectrum):
    """Sets something in plot calling callable_(fmt.format(spectrum) if fmt is not empty"""
    if fmt:
        callable_(fmt.format(spectrum))

class PlotSpectrumSetup(object):
    """

    Args:
        fmt_xlabel: format string for x-label
        fmt_ylabel: format string for y-label
        fmt_title: format string for title
        ymin: (optional) force mininum y-value
        flag_legend: Whether to show legend in plot
    """
    def __init__(self, fmt_xlabel="{.xunit}", fmt_ylabel="{.yunit}", fmt_title="{.title}",
                 ymin=None, flag_legend=True, flag_xlabel=True, flag_ylabel=True):
        self.flag_xlabel = flag_xlabel
        self.flag_ylabel = flag_ylabel
        self.fmt_xlabel = fmt_xlabel
        self.fmt_ylabel = fmt_ylabel
        self.fmt_title = fmt_title
        self.ymin = ymin
        self.flag_legend = flag_legend

    def __repr__(self):
        return "{}('{}', '{}', '{}', {}, {})".format(self.__class__.__name__,self.fmt_xlabel,
          self.fmt_ylabel, self.fmt_title, self.ymin, self.flag_legend)


_default_setup = PlotSpectrumSetup()


def plot_spectra_stacked(ss, title=None, num_rows=None, setup=_default_setup):
    """
    Plots one or more stacked in subplots sharing same x-axis.

    Args:
      ss: list of Spectrum objects
      title=None: window title
      num_rows=None: (optional) number of rows for subplot grid. If not passed,
        num_rows will be the number of plots, and the number of columns will be 1.
        If passed, number of columns is calculated automatically.
      setup: PlotSpectrumSetup object

    """

    draw_spectra_stacked(ss, title, num_rows, setup)
    plt.show()
    # return fig


def plot_spectra_overlapped(ss, title=None, setup=_default_setup):
    """
    Plots one or more spectra in the same plot.

    Args:
      ss: list of Spectrum objects
      title=None: window title
      setup: PlotSpectrumSetup object
    """

    plt.figure()
    draw_spectra_overlapped(ss, title, setup)
    plt.show()


def draw_spectra_overlapped(ss, title=None, setup=_default_setup):
    a99.format_BLB()
    if len(ss) > 0:
        xunit, yunit = None, None
        for i, s in enumerate(ss):
            if xunit is None:
                xunit = s.xunit
            else:
                if xunit != s.xunit:
                    raise RuntimeError("Spectra x-units do not match")

            if yunit is None:
                yunit = s.yunit
            else:
                if yunit != s.yunit:
                    raise RuntimeError("Spectra x-units do not match")

            ax = plt.gca()
            y = s.y
            ax.plot(s.x, y, label=str(s.title))

        # plt.ylabel('({})'.format(yunit))
        # **Note** Takes last spectrum as reference to mount x-label
        if setup.flag_xlabel and setup.fmt_xlabel:
            _set_plot(plt.xlabel, setup.fmt_xlabel, s)
        xmin, xmax, ymin_, ymax, xspan, yspan = calc_max_min(ss)
        ymin = ymin_ if setup.ymin is None else setup.ymin
        plt.xlim([xmin - xspan * _T, xmax + xspan * _T])
        plt.ylim([ymin - yspan * _T, ymax + yspan * _T])
        if setup.flag_legend:
            leg = plt.legend(loc=0)
            a99.format_legend(leg)
        plt.tight_layout()

    if title is not None:
        plt.gcf().canvas.set_window_title(title)


def plot_spectra_pieces_pdf(ss, aint=10, pdf_filename='pieces.pdf', setup=_default_setup):
    """
    Plots spectra, overlapped, in small wavelength intervals into a PDF file,
    one interval per page of the PDF file.

    Args:
      ss: list of Spectrum objects
      aint: wavelength interval for each plot
      pdf_filename: name of output file
      setup: PlotSpectrumSetup object

    **Note** overrides setup.fmt_xlabel; leaves y-labell and title blank
    """

    import f311.explorer as ex

    xmin, xmax, ymin_, ymax, _, yspan = calc_max_min(ss)
    ymin = ymin_ if setup.ymin is None else setup.ymin

    num_pages = int(math.ceil((xmax-xmin)/aint)) # rightmost point may be left out...or not
    # num_spectra = len(ss)

    a99.format_BLB()
    # pdf = matplotlib.backends.backend_pdf.PdfPages(pdf_filename)
    pdf = matplotlib.backends.backend_pdf.PdfPages(pdf_filename)
    logger = a99.get_python_logger()

    for h in range(num_pages):
        fig = plt.figure()
        lambda0 = xmin+h*aint
        lambda1 = lambda0+aint
        logger.info("Printing page {0:d}/{1:d} ([{2:g}, {3:g}])".format(h+1, num_pages, lambda0, lambda1))
        for i, s in enumerate(ss):
            s_cut = ex.cut_spectrum(s, lambda0, lambda1)
            ax = plt.gca()
            ax.plot(s_cut.x, s_cut.y, label=s.title)
        if setup.flag_xlabel and setup.fmt_xlabel:
            plt.xlabel('Wavelength (interval: [{0:g}, {1:g}])'.format(lambda0, lambda1))
        xspan = lambda1-lambda0
        ax.set_xlim([lambda0 - xspan * _T, lambda1 + xspan * _T])
        ax.set_ylim([ymin - yspan * _T, ymax + yspan * _T])
        if setup.flag_legend:
            leg = plt.legend(loc=0)
            a99.format_legend(leg)
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()

    # for fig in xrange(1, figure().number): ## will open an empty extra figure :(
    #     pdf.savefig( fig )
    pdf.close()
    logger.info("File {0!s} successfully created.".format(pdf_filename))


def plot_spectra_pages_pdf(ss, pdf_filename='pages.pdf', setup=_default_setup):
    """
    Plots spectra into a PDF file, one spectrum per page.

    Splits into several pieces of width

    Args:
      ss: list of Spectrum objects
      pdf_filename: name of output file
    """
    logger = a99.get_python_logger()
    xmin, xmax, ymin_, ymax, xspan, yspan = calc_max_min(ss)
    ymin = ymin_ if setup.ymin is None else setup.ymin
    num_pages = len(ss)
    a99.format_BLB()
    pdf = matplotlib.backends.backend_pdf.PdfPages(pdf_filename)
    for i, s in enumerate(ss):
        title = s.title
        fig = plt.figure()
        plt.plot(s.x, s.y, c=_FAV_COLOR)
        if setup.flag_xlabel and setup.fmt_xlabel:
            _set_plot(plt.xlabel, setup.fmt_xlabel, s)
        if setup.flag_ylabel and setup.fmt_ylabel:
            _set_plot(plt.ylabel, setup.fmt_ylabel, s)
        _set_plot(plt.title, setup.fmt_title, s)
        plt.xlim([xmin-xspan*_T, xmax+xspan*_T])
        plt.ylim([ymin-yspan*_T, ymax+yspan*_T])
        plt.tight_layout()
        plt.subplots_adjust(top=0.94) # workaround for cropped title
        logger.info("Printing page {0:d}/{1:d} ('{2!s}')".format(i+1, num_pages, title))
        pdf.savefig(fig)
        plt.close()
    pdf.close()
    logger.info("File {0!s} successfully created.".format(pdf_filename))


def calc_max_min(ss):
    """"Calculates (x, y) (max, min) for a list of Spectrum objects.

    Returns (xmin, xmax, ymin, ymax, xspan, yspan)
    """
    xmin, xmax, ymin, ymax = 1e38, -1e38, 1e38, -1e38
    for s in ss:
        assert isinstance(s, ft.Spectrum)
        if len(s.x) > 0:
            xmin, xmax = min(min(s.x), xmin), max(max(s.x), xmax)
            ymin, ymax = min(min(s.y), ymin), max(max(s.y), ymax)
    xspan = xmax-xmin
    yspan = ymax - ymin
    return xmin, xmax, ymin, ymax, xspan, yspan


def draw_spectra_stacked(ss, title=None, num_rows=None, setup=_default_setup):
    """Same as plot_spectra_stacked(), but does not call plt.show(); returns figure"""
    n = len(ss)
    assert n > 0, "ss is empty"
    if not num_rows:
        num_rows = n
        num_cols = 1
    else:
        num_cols = int(np.ceil(float(n) / num_rows))
    a99.format_BLB()

    fig, axarr = plt.subplots(num_rows, num_cols, sharex=True, squeeze=False)
    xmin = 1e38
    xmax = -1e38
    i, j = -1, num_cols
    xunit, yunit = None, None
    any_span = False
    for s in ss:
        j += 1
        if j >= num_cols:
            i += 1
            if i >= num_rows:
                break
            j = 0
        assert isinstance(s, ft.Spectrum)
        ax = axarr[i, j]
        y = s.y
        ax.plot(s.x, y)
        ymin_, ymax = ax.get_ylim()
        ymin_now = ymin_ if setup.ymin is None else setup.ymin
        ax.set_ylim([ymin_now, ymin_now + (ymax - ymin_now) * (1 + _T)])  # prevents top of line from being hidden by plot box

        _set_plot(ax.set_ylabel, setup.fmt_ylabel, s)
        _set_plot(ax.set_title, setup.fmt_title, s)

        if len(s.x) > 0:
            xmin, xmax = min(min(s.x), xmin), max(max(s.x), xmax)
            any_span = True

        if xunit is None:
            xunit = s.xunit
        else:
            if xunit != s.xunit:
                raise RuntimeError("Spectra x-units do not match")

        if yunit is None:
            yunit = s.yunit
        else:
            if yunit != s.yunit:
                raise RuntimeError("Spectra x-units do not match")

    if any_span:
        span = xmax - xmin
        ax.set_xlim([xmin - span * _T, xmax + span * _T])
    for j in range(num_cols):
        ax = axarr[num_rows - 1, j]
        if setup.flag_xlabel and setup.fmt_xlabel:
            _set_plot(ax.set_xlabel, setup.fmt_xlabel, s)
    plt.tight_layout()
    if title is not None:
        fig.canvas.set_window_title(title)
    return fig
