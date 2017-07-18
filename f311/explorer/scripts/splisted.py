#!/usr/bin/env python

"""Spectrum List Editor"""

import sys
import argparse
import a99
import f311.filetypes as ft
import f311.explorer as ex
import logging
import f311.explorer as ex
import f311.filetypes as ft

a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('fn', type=str, help="file name, supports '%s' only at the moment" %
                                             (ft.FileSpectrumList.description,), nargs='?')
    args = parser.parse_args()

    app = a99.get_QApplication([])
    form = ex.XFileSpectrumList()

    if args.fn is not None:
        form.load_filename(args.fn)

    form.show()
    sys.exit(app.exec_())
