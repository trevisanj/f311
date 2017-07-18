#!/usr/bin/env python

"""F311 Explorer --  list, visualize, and edit data files (_à la_ File Manager)"""

import a99
import f311.filetypes as ft
import f311.explorer as ex
import f311.explorer as ex
import sys
import argparse
import logging


a99.logging_level = logging.INFO
a99.flag_log_file = True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('dir', type=str, help='directory name', default='.', nargs='?')
    args = parser.parse_args()

    app = a99.get_QApplication([])
    form = ex.XExplorer(None, args.dir)
    form.show()
    a99.place_center(form)
    sys.exit(app.exec_())
