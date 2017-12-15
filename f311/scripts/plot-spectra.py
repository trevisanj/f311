#!/usr/bin/env python
"""
Plots spectra on screen or creates PDF file

It can work in four different modes:

a) grid of sub-plots, one for each spectrum (default mode)
   Example:
   plot-spectra.py flux.norm.nulbad measured.fits

b) single plot with all spectra overlapped ("--ovl" option)
   Example:
   > plot-spectra.py --ovl flux.norm.nulbad measured.fits

c) PDF file with a small wavelength interval per page ("--pieces" option).
   This is useful to flick through a large wavelength range.
   Example:
   > plot-spectra.py --pieces --aint 7 flux.norm.nulbad measured.fits

d) PDF file with one spectrum per page ("--pages" option).
   Example:
   > plot-spectra.py --pages flux.*

Types of files supported:

  - pfant output, e.g., flux.norm;
  - nulbad output, e.g., flux.norm.nulbad;
  - 2-column "lambda-flux" generic text files;
  - FITS files.

"""
import argparse
import a99
import logging
import glob
import f311.explorer as ex
import f311.filetypes as ft
import f311

a99.logging_level = logging.INFO
a99.flag_log_file = True

DEFAULT_FN_OUTPUT = '(plot-spectra-<xxxx>.pdf)'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
    )

    parser.add_argument('fn', type=str, nargs='+',
     help='name of spectrum file(s) (many types supported) '
          '(wildcards allowed, e.g., "flux.*")')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--ovl', help='Overlapped graphics', action="store_true")
    group.add_argument('--pieces', help='If set, will generate a PDF file with '
     'each page containing one "piece" of the spectra of length'
     'given by the --aint option.', action="store_true")
    group.add_argument('--pages', help='If set, will generate a PDF file with '
     'one spectrum per page', action="store_true")
    # parser.add_argument('--ovl', help='Overlapped graphics', action="store_true")
    # parser.add_argument('--pieces', help='If set, will generate a PDF file with '
    #  'each page containing one "piece" of the spectra of length'
    #  'given by the --aint option.', action="store_true")
    # parser.add_argument('--pages', help='If set, will generate a PDF file with '
    #  'one spectrum per page', action="store_true")
    parser.add_argument('--aint', type=float, nargs='?', default=10,
     help='length of each piece-plot in wavelength units (used only if --pieces)')
    parser.add_argument('--fn_output', nargs='?', default=DEFAULT_FN_OUTPUT, type=str,
                        help='PDF output file name (used only if --pieces)')
    parser.add_argument('--ymin', nargs='?', default='(automatic)', type=str,
     help='Minimum value for y-axis')
    parser.add_argument('-r', '--num_rows', nargs='?', default='(automatic)', type=str,
     help='Number of rows in subplot grid')

    args = parser.parse_args()

    ymin = None if args.ymin == "(automatic)" else float(args.ymin)
    num_rows = None if args.num_rows == "(automatic)" else int(args.num_rows)

    # Compiles list of file names.
    # Each item in args.fn list may have wildcards, and these will be expanded
    # into actual filenames, then duplicates are eliminated
    patterns = args.fn
    _ff = []
    for pattern in patterns:
        _ff.extend(glob.glob(pattern))
    ff = []
    for f in _ff:
        if f not in ff:
            ff.append(f)

    # classes = [FileSpectrumPfant, FileSpectrumNulbad, FileSpectrumXY, FileSpectrumFits]

    ss = []
    flag_ok = False
    for x in ff:
        print("Reading file '{0!s}'...".format(x))
        f = f311.load_with_classes(x, f311.classes_sp())
        if f is None:
            a99.print_error("... type not recognized, sorry")
        else:
            print("... successfully read using reader {0!s}.".format(f.__class__.__name__))
            ss.append(f.spectrum)


    # # Making name for output file
    if args.fn_output == DEFAULT_FN_OUTPUT:
        if len(ss) == 1:
            # If there is only one spectrum, makes output PDF filename using spectrum name
            prefix = "plot-spectra-"+ss[0].filename
        else:
            prefix = "plot-spectra"
        fn_output = a99.new_filename(prefix, "pdf")
    else:
        fn_output = args.fn_output

    if len(ss) == 0:
        a99.print_error("Nothing to plot!")
    else:
        setup = ex.PlotSpectrumSetup(ymin=ymin)
        if len(ss) == 1:
            # No need for legend in plot if there is only one spectrum.
            # Spectrum filename will be part of PDF filename anyway
            setup.flag_legend = False

        if args.pieces:
            ex.plot_spectra_pieces_pdf(ss, aint=args.aint, pdf_filename=fn_output, setup=setup)
        elif args.pages:
            ex.plot_spectra_pages_pdf(ss, pdf_filename=fn_output, setup=setup)
        else:
            if args.ovl:
                ex.plot_spectra_overlapped(ss, "", setup=setup)
            else:
                ex.plot_spectra_stacked(ss, "", setup=setup, num_rows=num_rows)
