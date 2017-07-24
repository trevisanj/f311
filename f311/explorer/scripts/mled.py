#!/usr/bin/env python

"""Molecular lines file editor."""

import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import argparse
import logging
import f311.pyfant as pf
import a99
import f311.filetypes as ft
import f311.explorer as ex


if __name__ == "__main__":
    a99.logging_level = logging.INFO
    a99.flag_log_file = True

    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='molecules file name',
                        default=ft.FileMolecules.default_filename, nargs='?')
    args = parser.parse_args()

    m = ft.FileMolecules()
    m.load(args.fn)
    app = a99.get_QApplication([])
    form = ex.XFileMolecules()
    form.show()
    form.load(m)
    sys.exit(app.exec_())











