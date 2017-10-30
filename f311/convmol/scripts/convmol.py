#!/usr/bin/env python

"""Conversion of molecular lines data to PFANT format"""

import sys
import argparse
import a99
import logging
import os
import f311.filetypes as ft
import f311.convmol as cm


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":

    deffn = ft.FileMolDB.default_filename

    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('--fn_moldb', type=str, help='File name for {}'.format(ft.FileMolDB.description),
                        default=ft.FileMolDB.default_filename, nargs='?')
    parser.add_argument('--fn_molconsts', type=str, help='File name for {}'.format(ft.FileMolConsts.description),
                        default=ft.FileMolConsts.default_filename, nargs='?')
    parser.add_argument('--fn_config', type=str, help='File name for {}'.format(ft.FileConfigConvMol.description),
                        default=ft.FileConfigConvMol.default_filename, nargs='?')
    args = parser.parse_args()

    _fnfn = [args.fn_moldb, args.fn_molconsts, args.fn_config]
    fnfn = [None if fn is None or not os.path.isfile(fn) else fn for fn in _fnfn]


    # if args.fn == deffn and not os.path.isfile(deffn):
    #     args.fn = None

    m = None
    # if args.fn is not None:
    #     m = ft.FileMolDB()
    #     m.load(args.fn)
    app = a99.get_QApplication([])
    form = cm.XConvMol()
    form.load_many(fnfn)
    form.show()
    sys.exit(app.exec_())


