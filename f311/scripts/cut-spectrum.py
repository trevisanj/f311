#!/usr/bin/env python
"""
Cuts spectrum file to wavelength interval specified

Resulting spectrum Saved in 2-column ASCII format

The interval is [llzero, llfin]
"""

import argparse
import logging
import sys
import a99
import f311

a99.logging_level = logging.INFO

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

    sp = f311.load_spectrum(args.fn_input[0])
    if not sp:
        print("File '{0!s}' not recognized as a spectrum file.".format(args.fn_input[0]))
        sys.exit()

    m = min(sp.x)
    M = max(sp.x)

    print("Original interval: [{0:g}, {1:g}]".format(m, M))
    print("New interval: [{0:g}, {1:g}]".format(args.llzero[0], args.llfin[0]))

    f = f311.FileSpectrumXY()
    f.spectrum = f311.cut_spectrum(sp, args.llzero[0], args.llfin[0])
    f.save_as(args.fn_output[0])
    print("Successfully created file '{0!s}'".format(args.fn_output[0]))
