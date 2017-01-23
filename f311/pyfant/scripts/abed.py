#!/usr/bin/env python3

"""Abundances file editor"""

import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import argparse
import f311.pyfant as pf
import a99
import logging


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='abundances file name', default='abonds.dat', nargs='?')
    args = parser.parse_args()

    m = pf.FileAbonds()
    m.load(args.fn)
    app = a99.get_QApplication([])
    form = pf.XFileAbonds()
    form.show()
    form.load(m)
    sys.exit(app.exec_())
