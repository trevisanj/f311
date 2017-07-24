#!/usr/bin/env python

"""Abundances file editor"""

import sys
import argparse
import logging
import f311.filetypes as ft
import f311.explorer as ex
import a99


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='abundances file name', default='abonds.dat', nargs='?')
    args = parser.parse_args()

    m = ft.FileAbonds()
    m.load(args.fn)
    app = a99.get_QApplication([])
    form = ex.XFileAbonds()
    form.show()
    form.load(m)
    sys.exit(app.exec_())
