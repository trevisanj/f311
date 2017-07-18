#!/usr/bin/env python

"""
Prints table of diatomic molecular constants

If ID is specified, prints data for single molecule;
otherwise, prints full table
"""

import argparse
import logging
import a99


a99.logging_level = logging.INFO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('ID', type=str, help='HITRAN Molecule ID',
                        default='(all)', nargs='?')
    args = parser.parse_args()

    kwargs = {}
    if not args.ID == "(all)":
        kwargs["molecule.ID"] = args.ID

    pf.hitrandb.print_isotopologues(**kwargs)