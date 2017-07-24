#!/usr/bin/env python

"""
Prints table of diatomic molecular constants

If formula is specified, prints data for single formula;
otherwise, prints full table
"""

import f311.convmol as cm
import argparse
import logging
import a99


pf.logging_level = logging.INFO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('-f', type=str, help='Formula of molecule',
                        default='(all)', nargs='?')
    parser.add_argument('-id', type=str, help='State internal ID (second column when printing the whole table)',
                        default=None, nargs='?')
    args = parser.parse_args()

    kwargs = {}
    if not args.f == "(all)":
        kwargs["formula"] = args.f
    if args.id is not None:
        kwargs["state.id"] = args.id

    cm.moldb.print_states(**kwargs)