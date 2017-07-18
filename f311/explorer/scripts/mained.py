#!/usr/bin/env python

"""Main configuration file editor."""

import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import argparse
import logging
import f311.explorer as ex
import a99
import f311.filetypes as ft


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='main configuration file name', default='main.dat', nargs='?')
    args = parser.parse_args()

    m = ft.FileMain()
    m.load(args.fn)
    app = a99.get_QApplication([])
    form = ex.XFileMain()
    form.load(m)
    form.show()
    sys.exit(app.exec_())
