#!/usr/bin/env python
"""
Retrieves and prints a table of molecular constants from the NIST Chemistry Web Book [NISTRef]

To do so, it uses web scraping to navigate through several pages and parse the desired information
from the book web pages.

It does not provide a way to list the molecules yet, but will give an error if the molecule is not
found in the NIST web book.

Example:

    print-nist.py OH

**Note** This script was designed to work with **diatomic molecules** and may not work with other
         molecules.

**Warning** The source material online was known to contain mistakes (such as an underscore instead
            of a minus signal to indicate a negative number). We have identified a few of these,
            and build some workarounds. However, we recommend a close look at the information parsed
            before use.

**Disclaimer** This script may stop working if the NIST people update the Chemistry Web Book.

References:

[NISTRef] http://webbook.nist.gov/chemistry/
"""


import tabulate
import sys
import a99
import logging
import argparse
import f311.convmol as cm


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=a99.SmartFormatter)
    parser.add_argument('formula', type=str, help='NIST formula', nargs=1)
    args = parser.parse_args()

    data, header, title = cm.get_nist_webbook_constants(args.formula)
    print("\n*** {} ***\n".format(title))
    print(tabulate.tabulate(data, header))


