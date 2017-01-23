#!/usr/bin/env python3


"""Retrieves molecular constants from NIST Web Book for a particular molecule

Example:

    get-nist-mol.py OH

"""


import tabulate
import sys
from pyfant.convmol.nistbot import get_nist_webbook_constants
import a99
import logging
import argparse


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=a99.SmartFormatter)
    parser.add_argument('formula', type=str, help='NIST formula', nargs=1)
    args = parser.parse_args()

    data, header, title = get_nist_webbook_constants(args.formula)
    print("\n*** {} ***\n".format(title))
    print(tabulate.tabulate(data, header))


