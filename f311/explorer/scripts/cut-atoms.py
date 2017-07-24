#!/usr/bin/env python
"""
Cuts atomic lines file to wavelength interval specified

The interval is [llzero, llfin]
"""

# TODO add this functionality to ated.py


import argparse
import logging
import a99
import f311.filetypes as ft
import f311.explorer as ex
import f311.filetypes as ft


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
     )
    parser.add_argument('llzero', type=float, nargs=1,
     help='lower wavelength boundary (angstrom)')
    parser.add_argument('llfin', type=float, nargs=1,
     help='upper wavelength boundary (angstrom)')
    parser.add_argument('fn_input', type=str, help='input file name', nargs=1)
    parser.add_argument('fn_output', type=str, help='output file name', nargs=1)

    args = parser.parse_args()

    file_atoms = ft.FileAtoms()
    file_atoms.load(args.fn_input[0])

    m = min([min(a.lambda_) for a in file_atoms.atoms])
    M = max([max(a.lambda_) for a in file_atoms.atoms])

    print("Original interval: [%g, %g]" % (m, M))
    print("New interval: [%g, %g]" % (args.llzero[0], args.llfin[0]))

    file_atoms.cut(args.llzero[0], args.llfin[0])
    file_atoms.save_as(args.fn_output[0])
    print("Successfully created file '%s'" % args.fn_output[0])
