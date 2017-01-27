#!/usr/bin/env python3
"""
Opens several windows to show what is inside a NEWMARCS grid file.
"""

import argparse
import a99
import logging


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
   description=a99.VisModCurves.__doc__,
   formatter_class=a99.SmartFormatter
   )

  parser.add_argument('fn', type=str, help='NEWMARCS grid file name')

  args = parser.parse_args()

  m = ft.FileModBin()
  m.load(args.fn)


  v = a99.VisModCurves()
  v.title = args.fn
  v.use(m)
