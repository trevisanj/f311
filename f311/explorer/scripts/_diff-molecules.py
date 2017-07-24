#!/usr/bin/env python

"""
Compares two molecular lines files and prints report with differences
"""

import a99
import tabulate
import logging
import argparse
import f311.filetypes as ft


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
     )
    parser.add_argument('fn1', type=str, help='input file name', nargs=1)
    parser.add_argument('fn2', type=str, help='output file name', nargs=1)

    args = parser.parse_args()

    fn1 = args.fn1[0]
    fn2 = args.fn2[0]

    fa = ft.FileMolecules()
    fa.load(fn1)

    fb = ft.FileMolecules()
    fb.load(fn2)

    data = []
    header = [fn1, fn2]


    def append_data(objname, attrname, value0, value1):
        """Appends difference"""
        data.append(["{}.{} = {}".format(objname, attrname, value0),
                     "{}.{} = {}".format(objname, attrname, value1)])

    def check_append(objname, attrname, obj0, obj1):
        """Checks if attributes match and add data entry otherwise"""
        value0 = obj0.__getattribute__(attrname)
        value1 = obj1.__getattribute__(attrname)
        if value0 != value1:
            append_data(objname, attrname, value0, value1)

    check_append("file", "num_lines", fa, fb)

    to_check = ["formula", "nv", "num_lines", "fe", "do", "mm", "am", "bm", "ua", "ub", "te",
                "cro", "s", ]

    for i, (ma, mb) in enumerate(zip(fa, fb)):
        for attr in to_check:
            check_append("mol[{}]".format(i), attr, ma, mb)

    print(tabulate.tabulate(data, header))
