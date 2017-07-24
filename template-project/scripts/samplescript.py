#!/usr/bin/env python
# Sample script
"""Echoes argument backwards"""

import a99
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
    parser.add_argument('arg', type=str, help='directory name', default='John Smith')
    args = parser.parse_args()

    print("".join(reversed(args.arg)))
