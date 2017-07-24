#!/usr/bin/env python

"""
Create several .splist (spectrum list) files from WebSim-COMPASS output files; groups spectra that share same wavelength vector

All spectra in each .splist file will have the same wavelength vector
"""


import argparse
import logging
from f311 import aosss
import a99


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
    )

    parser.add_argument('--stage', type=str, nargs='?', default="spintg",
     help="Websim-Compass pipeline stage (will collect files named, e.g., C000793_<stage>.fits)")

    args = parser.parse_args()

    aosss.create_spectrum_lists(".", args.stage)



