__all__ = ["create_simulation_report", "create_index"]


import os
from astropy.io import fits
from matplotlib import pyplot as plt
from .util import *
import numpy as np
import traceback
import glob
import a99
import f311.filetypes as ft
import f311.explorer as ex


def create_index(dir_="."):
    """[re]created 'index.html' of report*"""
    ff = glob.glob(os.path.join(dir_, "report-*.html"))
    ff.sort()

    with open(os.path.join(dir_, "index.html"), "w") as html:
        html.write(_head("List of Reports"))
        html.write("<body>")
        for f in ff:
            f = os.path.basename(f)
            html.write('<p><a href="{0}">{0}</a>'.format(f))
        html.write("</body></html>")


# # HTML fragment generation routines
# Block routines (e.g., head, h1) result should always end with a "\n".
# Inline tags, NOT.


def _head(title):
    """Returns the "head" section of HTML"""

    return """<!DOCTYPE html>
<html>
<head>
  <title>%s</title>
</head>
""" % title


def _h(title, n=1):
    """Creates "h<n>" tag"""
    return "<h%d>%s</h%d>\n" % (n, title, n)


# FITS files: <simid>+"_"+_fitss[i]+".fits"
FILE_KEYWORDS = ["cube_hr", "cube_seeing", "ifu_noseeing", "mask_fiber_in_aperture",
          "reduced", "reduced_snr", "sky", "skysub", "spintg", "spintg_noseeing",
          "therm"]


def _color(s, color):
    """Returns inline colored text"""
    return '<span style="color: %s">%s</span>' % (color, s)


def create_simulation_report(simid, dir_="."):
    """Creates HTML output and several PNG files with coherent naming

    Args:
        simid: simulation ID. This should be a string starting with a "C", e.g., "C000793"
        dir_: directory containing the simulation ouput files

    Returns:
        str: name of output file created, which will be ``<dir_>/report-<simid>.html``
    """

    if simid[0] != "C":
        raise RuntimeError("Simulation ID must start with a 'C' letter")

    # # Setup

    # file_prefix: common start to all filenames generated
    file_prefix = os.path.join(dir_, "report-"+simid)
    fn_output = file_prefix + ".html"
    # f_fn_fits = lambda middle: os.path.join(dir_, "%s_%s.fits" % (simid, middle))
    fn_log = os.path.join(dir_, "%s.out" % simid)
    fn_par = os.path.join(dir_, "%s.par" % simid)
    flag_log = os.path.isfile(fn_log)
    flag_par = os.path.isfile(fn_par)


# TODO probably load_par separate
# TODO probably load_all_fits() instead of load_bulk()
    items = load_bulk(simid, dir_)

    # My first generator!!!
    def gen_fn_fig():
        cnt = 0
        while True:
            yield "%s-%03d.png" % (file_prefix, cnt)
            cnt += 1
    next_fn_fig = gen_fn_fig()

    # # HTML Generation

    with open(fn_output, "w") as html:
        html.write(_head("Simulation %s" % simid))
        html.write("<body>")
        html.write(_h("Simulation # %s" % simid))

        html.write(_h("1. File list", 2))
        l_s = ["<pre>\n"]
        for item in items:
            l_s.append(item.filename+(" (not present)" if not item.flag_exists else "")+"\n")

        # ".par" file is an extra case
        l_s.append(fn_par)
        if not os.path.isfile(fn_par):
            l_s.append(" (not present)")
        l_s.append("\n")

        # Log file is an extra case
        l_s.append(fn_log)
        if not os.path.isfile(fn_log):
            l_s.append(" (not present)")
        l_s.append("\n")

        l_s.append("</pre>\n")
        html.write("".join(l_s))

        html.write(_h("2. Simulation specification", 2))
        if  flag_par:
            flag_par_ok = True
            try:
                filepar = ft.FilePar()
                filepar.load(fn_par)
            except Exception as E:
                flag_par_ok = False
                a99.get_python_logger().exception("Failed to load file '%s'" % fn_par)
                html.write("(" + str(E) + ")")

            if flag_par_ok:
                html.write('<table cellspacing=0 cellpadding=3 style="border: 6px solid #003000;">\n')
                for kw, va in list(filepar.params.items()):
                    html.write('<tr><td style="border-bottom: 1px solid #003000; font-weight: bold">%s</td>\n' % kw)
                    html.write('<td style="border-bottom: 1px solid #003000;">%s</td></tr>\n' % va)
                html.write("</table>\n")
        else:
            html.write(_color("File '%s' not present" % fn_par, "red"))


        # html.write(_h("2. FITS headers", 2))
        html.write(_h("3. FITS files", 2))
        html.write('<table cellspacing=0 cellpadding=3 style="border: 6px solid #003000;">\n')
        for item in items:
            html.write('<tr>\n<td colspan=2 style="vertical-align: top; border-bottom: 3px solid #003000;">\n')
            html.write("<b>%s</b>" % os.path.basename(item.filename))
            html.write('</td>\n</tr>\n')

            html.write('<tr>\n<td style="vertical-align: top; border-bottom: 6px solid #003000;">\n')
            try:
                # Opens as fits to dump header
                with fits.open(item.filename) as hdul:
                    hdul.verify()
                    try:
                        s_h = repr(hdul[0].header)
                    except:
                        # Apparently, on the second time, it works if does not on the first time
                        s_h = repr(hdul[0].header)
                html.write("<pre>%s</pre>\n" % s_h)
            except:
                a99.get_python_logger().exception("Failed to dump header from file '%s'" % item.filename)
                html.write(_color("Header dump failed", "red"))
            html.write("</td>\n")


            print(("Generating visualization for file '%s' ..." % item.filename))
            html.write('<td style="vertical-align: top; border-bottom: 6px solid #003000; text-align: center">\n')
            try:
                fig = None
                FIGURE_WIDTH = 570
                if isinstance(item.fileobj, ft.FileFullCube) and (not "cube_seeing" in item.filename):
                    # note: skips "ifu_seeing" because it takes too long to renderize
                    fig = plt.figure()
                    ax = fig.gca(projection='3d')
                    sparsecube = ft.SparseCube()
                    sparsecube.from_full_cube(item.fileobj.wcube)
                    ex.draw_cube_3d(ax, sparsecube)
                    a99.set_figure_size(fig, FIGURE_WIDTH, 480. / 640 * FIGURE_WIDTH)
                    fig.tight_layout()
                elif isinstance(item.fileobj, ft.FileSpectrum):
                    if item.keyword == "spintg":
                        sp_ref = item.fileobj.spectrum
                    fig = ex.draw_spectra([item.fileobj.spectrum])
                    a99.set_figure_size(fig, FIGURE_WIDTH, 270. / 640 * FIGURE_WIDTH)
                    fig.tight_layout()
                elif isinstance(item.fileobj, ft.FileFits):
                    if item.keyword == "mask_fiber_in_aperture":
                        fig = _draw_mask(item.fileobj)
                    elif item.keyword == "cube_seeing":
                        fig = _draw_field(item.fileobj)

                if fig:
                    fn_fig = next(next_fn_fig)
                    # print "GONNA SAVE FIGURE AS "+str(fn_fig)
                    fig.savefig(fn_fig)
                    plt.close()
                    html.write('<img src="%s"></img>' % fn_fig)
                elif item.fileobj:
                    html.write("(visualization not available for this file (class: %s)" % item.fileobj.__class__.description)
                else:
                    # TODO I already have the error information, so can improve this
                    html.write("(could not load file)")

                # html.write("hello")

            except Exception as E:
                a99.get_python_logger().exception("Failed to load file '%s'" % item.filename)
                html.write(_color("Visualization failed: "+str(E), "red"))
                html.write('<pre style="text-align: left">\n'+traceback.format_exc()+"</pre>\n")
            html.write("</td>\n")
            html.write("</tr>\n")
        html.write("</table>\n")

        html.write(_h("4. Log file dump", 2))
        if  flag_log:
            html.write("<pre>\n")
            try:
                with open(fn_log, "r") as file_log:
                    html.write(file_log.read())
            except Exception as E:
                a99.get_python_logger().exception("Failed to dump log file '%s'" % fn_log)
                html.write("("+str(E)+")")
            html.write("</pre>\n")
        else:
            html.write(_color("File '%s' not present" % fn_log, "red"))


    return fn_output


def _draw_mask(filefits):
    """Draws the image for the Cxxxxx_mask_fiber_in_aperture.fits file. Returns figure"""
    hdu = filefits.hdulist[0]
    fig = plt.figure()
    plt.imshow(hdu.data)
    plt.xlabel("pixel-x")
    plt.ylabel("pixel-y")
    HEIGHT = 300.
    nr, nc = hdu.data.shape
    width = HEIGHT/nr*nc
    a99.set_figure_size(fig, width, HEIGHT)
    plt.tight_layout()
    return fig


def _draw_field(filefits):
    """Draws data cube in grayscale. Values are calculated as 2-vector-norm"""
    hdu = filefits.hdulist[0]
    data = hdu.data
    grayscale = np.linalg.norm(data, 2, 0)
    fig = plt.figure()
    plt.imshow(grayscale, cmap='Greys_r')
    plt.xlabel("pixel-x")
    plt.ylabel("pixel-y")
    HEIGHT = 300.
    nr, nc = grayscale.shape
    width = HEIGHT/nr*nc
    a99.set_figure_size(fig, width, HEIGHT)
    plt.tight_layout()
    return fig

