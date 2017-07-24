#!/usr/bin/env python


"""
Downloads WebSim-COMPASS simulations

Based on shell script by Mathieu Puech

**Note** Skips simulations for existing files in local directory starting with
         that simulation ID.
         Example: if it finds file(s) "C001006*", will skip simulation C001006

**Note** Does not create any directory (actually creates it but deletes later).
         All files stored in local directory!

**Note** Will work only on if os.name == "posix" (Linux, UNIX ...)
"""


import os
import argparse
import sys
import glob
import logging
from f311 import aosss
import a99


a99.logging_level = logging.INFO
a99.flag_log_file = True



def print2(*args):
  a99.get_python_logger().info(*args)


if __name__ == "__main__":
    if os.name != "posix":
        print2("OS is '"+os.name+"', this script is only for 'posix' OS's, sorry.")
        sys.exit()

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=a99.SmartFormatter)
    parser.add_argument('--max', metavar='N', type=int, default=100,
                        help='Maximum number of simulations to get')
    parser.add_argument('--stage', type=str, nargs='?', default="all",
     help="Websim-Compass pipeline stage: if specified, will download files named, e.g., "
          "C000793_<stage>.fits (**note**: .par and .out files are always downloaded)")

    parser.add_argument('numbers', metavar='N', type=str, nargs='+',
                     help='List of simulation numbers (single value and ranges accepted, e.g. 1004, 1004-1040)')
    args = parser.parse_args()

    simids = aosss.compile_simids(args.numbers)
    print2("List of simulation IDs: "+", ".join(simids))

    if len(simids) > args.max:
        print2("Number of simulations to download (%d) exceeds maximum number (%d)" % (len(simids), args.max))
        print2("Use --max option to raise this maximum number")
        sys.exit()

    # Part based on Mathieu Puech's script
    #
    # wget options explained:
    #   -v       -- verbose
    #   -P       --  prefix: directory to save files to
    #   -A       -- accept: accept only certain file types
    #   -r       -- recursive
    #   -l1      -- specify maximum recursion level depth
    #   -e       -- execute a command as if it were part of .wgetrc
    #   -np      -- (--no-parent)
    #               do not ever ascend to the parent directory when retrieving recursively
    site = "http://websim-compass.obspm.fr/wcompass"
    for simid in simids:
        ff = glob.glob("%s*" % simid)
        if len(ff) > 0:
            print2("Files found starting with '%s', skipping this download" % simid)
        print2("Downloading %s simulation files..." % simid)
        # os.system("wget -v -r -l1 -np -nd -erobots=off -P %s %s/%s/" % (simid, site, simid))
        os.system("wget -v -P %s %s/%s.out" % (simid, site, simid))
        os.system("wget -v -P %s %s/%s.par" % (simid, site, simid))

        if args.stage == "all":
            os.system("wget -v -r -l1 -np -nd -erobots=off -P %s -A.fits -A.par %s/%s/" % (simid, site, simid))
        else:
            os.system("wget -v -P {0} {1}/{0}/{0}_{2}.fits".format(simid, site, args.stage))

        os.system("mv %s/* ." % simid)
        os.system("rm -r %s" % simid)

