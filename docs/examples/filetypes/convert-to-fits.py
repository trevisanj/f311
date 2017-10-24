#!/usr/bin/env python
"""Converts 1D spectral file of any supported type to FITS format.

The new file is saved with name "<original-filename>.fits".

TODO handle non-equally spaced wavelength values
"""

import f311.filetypes as ft
import sys
import logging

if __name__ == "__main__":
    if len(sys.argv) < 2 or any([x.startswith("-") for x in sys.argv[1:]]):
        print(__doc__+"\nUsage:\n\n    convert-to-fits.py filename0 [filename1 [filename2 [...]]]\n")
        sys.exit()

    for filename in sys.argv[1:]:
        print("Converting file '{}'...".format(filename))

        try:
            spectrum = ft.load_spectrum(filename)

            if spectrum is None:
                print("File '{}' not recognized as a 1D spectral file".format(filename))
                continue

            filename_new = filename+".fits"

            fnew = ft.FileSpectrumFits()
            fnew.spectrum = spectrum
            fnew.save_as(filename_new)

            print("Successfully saved '{}'".format(filename_new))
        except:
            logging.exception("Error converting file '{}'".format(filename))