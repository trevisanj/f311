#!/usr/bin/env python

"""
Merges several PFANT molecular lines file into a single one
"""

import f311.pyfant as pf
import f311.filetypes as ft
import argparse
import os
import glob
import sys
import logging
import a99


a99.logging_level = logging.INFO
a99.flag_log_file = True


_AUTO = "(automatic)"
_PREFIX = "molecules-merged-"


def main(fns_input, fn_output):
    ffmol = []
    for fn in fns_input:
        fmol = ft.FileMolecules()
        try:
            fmol.load(fn)
            print("File '{}': {} molecule{}".format(
                fn,
                len(fmol),
                "" if len(fmol) == 1 else "s"
            ))
            ffmol.append(fmol)
        except:
            a99.get_python_logger().exception("Skipping file '{}'".format(fn))

    n = len(ffmol)

    fout = ft.FileMolecules()
    fout.titm = "Merge of {} file{}: {}".format(
        n,
        "s" if n != 1 else "",
        ", ".join([os.path.split(fmol.filename)[1] for fmol in ffmol]))

    for fmol in ffmol:
        fout.molecules.extend(fmol.molecules)
    print("Number of molecules in output: {}".format(len(fout)))

    if fn_output is None:
        fn_output = a99.new_filename(_PREFIX, ".dat")

    fout.save_as(fn_output)
    print("Saved file '{}'".format(fn_output))

if __name__ == "__main__":
    lggr = a99.get_python_logger()

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=a99.SmartFormatter)
    parser.add_argument("files", type=str, nargs="+", help="files specification: list of files, wildcards allowed")
    parser.add_argument("-o", "--fn_output", nargs="?", type=str, default=_AUTO,
     help="output filename. If not specified, creates file such as '{}.0000.dat'".format(_PREFIX))

    args = parser.parse_args()

    # Compiles list of file names.
    # Each item in args.fn list may have wildcards, and these will be expanded
    # into actual filenames, then duplicates are eliminated
    patterns = args.files
    _ff = []
    for pattern in patterns:
        _ff.extend(glob.glob(pattern))
    ff = []
    for f in _ff:
        if f not in ff:
            ff.append(f)

    # Output
    fn_output = None if args.fn_output == _AUTO else args.fn_output

    main(ff, fn_output)
