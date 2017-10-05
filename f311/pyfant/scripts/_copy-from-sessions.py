#!/usr/bin/env python

"""
Copies resulting spectra from session directories into given directory
"""

import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt
import a99
import glob
import os
import argparse
import f311.pyfant as pf
import f311.filetypes as ft
import f311.explorer as ex
import logging


a99.logging_level = logging.INFO
a99.flag_log_file = True

TEXT_DEFAULT_OUTPUT_DIRECTORY = '(auto)'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
     )

    pa = parser.add_argument
    pa('-o', "--dn_output", help='Output directory name', default=TEXT_DEFAULT_OUTPUT_DIRECTORY, type=str)
    pa('-p', "--prefix", help='Session prefix', default=pf.SESSION_PREFIX_SINGULAR, type=str)
    pa('-c', help='Copies continuum files (*.cont)', action="store_true")
    pa('-s', help='Copies spectrum files (*.spec)', action="store_true")
    pa('-n', help='Copies normalized spectrum files (*.norm)', action="store_true")

    args = parser.parse_args()

    dd = glob.glob(args.prefix+"*")
    dd.sort()

    pdf = matplotlib.backends.backend_pdf.PdfPages(args.fn_output)

    a99.format_BLB()

    for d in dd:
        name = d[8:]

        a99.get_python_logger().info("Looking into session '{}'...".format(name))

        norm_filenames = glob.glob(os.path.join(d, "*.norm"))
        if len(norm_filenames) == 0:
            continue

        for filename in norm_filenames:
            a99.get_python_logger().info("    File '{}'".format(filename))
            f = ft.FileSpectrumPfant()

            # Note: takes first .norm file that finds
            f.load(filename)

            ex.draw_spectra([f.spectrum])  #v.title = "%s" % name

            fig = plt.gcf()
            if args.samey:
                plt.ylim([0, 1.02])
            else:
                y = f.spectrum.y
                ymin, ymax = min(y), max(y)
                margin = .02*(ymax-ymin)
                plt.ylim([ymin-margin, ymax+margin])
            ax = plt.gca()
            p = ax.get_position()
            p.x0 = 0.11
            ax.set_position(p)  # Try to apply same position for all figures to improve flicking experience
            pdf.savefig(fig)
            plt.close()

    # for fig in xrange(1, figure().number): ## will open an empty extra figure :(
    #     pdf.savefig( fig )
    pdf.close()

