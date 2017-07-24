#!/usr/bin/env python

"""
Creates HTML reports from WebSim-COMPASS output files
"""


import sys
import argparse
import logging
import glob
import os
import logging
from f311 import aosss
import a99


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    lggr = a99.get_python_logger()

    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
    )

    parser.add_argument('--dir', nargs='?', default='.', type=str,
     help='Input directory')
    parser.add_argument('--max', metavar='N', type=int, default=100,
                        help='Maximum allowed number of reports')
    parser.add_argument('numbers', metavar='N', type=str, nargs='+',
                     help='List of simulation numbers (single value and ranges accepted, e.g. 1004, 1004-1040)')

    args = parser.parse_args()

    simids0 = aosss.compile_simids(args.numbers)

    # Checks which ones actually exist in directory
    simids = []
    for simid in simids0:
        ff = glob.glob(os.path.join(args.dir, "%s*" % simid))
        if len(ff) > 0:
            simids.append(simid)

    lggr.info("List of simulation IDs: " + ", ".join(simids))

    if len(simids) > args.max:
        lggr.critical("Number of simulations to report (%d) exceeds "
                                            "maximum number (%d)" % (len(simids), args.max))
        lggr.critical("Use --max option to raise this maximum number")
        sys.exit()

    for simid in simids:
        lggr.info("Creating report for simulation '{}'...".format(simid))
        fn_output = aosss.create_simulation_report(simid, args.dir)
        lggr.info("File '%s' created successfully" % fn_output)
