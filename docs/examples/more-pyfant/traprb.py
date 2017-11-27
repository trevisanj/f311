#!/usr/bin/env python
"""
Python script to run the TRAPRB code [Jarmain&McCallum1970]

[Jarmain&McCallum1970] Jarmain, W. R., and J. C. McCallum.
"TRAPRB: a computer program for molecular transitions." University of Western Ontario (1970)
"""

import f311.pyfant as pf
import argparse
import a99
import logging

a99.logging_level = logging.INFO
a99.flag_log_file = True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=a99.SmartFormatter)
    parser.add_argument('fn_input', type=str, help="Input filename")
    parser.add_argument('fn_output', type=str, nargs="?",
                        help="Output filename (default: '<input filename>.out'")
    args = parser.parse_args()

    fn_output = args.fn_output if args.fn_output is not None else args.fn_input+".out"

    e = pf.TRAPRB()
    e.fn_input = args.fn_input
    e.fn_output = args.fn_output
    e.run()
