#!/usr/bin/env python

"""F311 Explorer --  file manager-like application to list, visualize, and edit data files"""

import a99
import sys
import argparse
import logging
import f311


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
    form = f311.XExplorer(None, args.dir)
    form.show()
    a99.place_center(form)
    sys.exit(app.exec_())
