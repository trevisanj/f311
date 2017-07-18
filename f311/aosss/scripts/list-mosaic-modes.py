#!/usr/bin/env python


"""Lists MOSAIC Spectrograph modes"""


import argparse
import rows
import io
import logging
from f311 import aosss
import a99


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
    )
    parser.add_argument('search', nargs='?', default=None, type=str,
     help='Search string (optional) (e.g., "HMM")')

    args = parser.parse_args()

    modes = aosss.mosaic.modes

    search_str = args.search.lower() if args.search else None

    modes_filtered = [mode for mode in modes
                      if not args.search or
                         search_str in mode.name.lower() or
                         search_str in mode.abbreviation.lower()]

    dicts = [mode.to_dict() for mode in modes_filtered]

    table = rows.import_from_dicts(dicts)
    fobj = io.StringIO()
    rows.export_to_txt(table, fobj)
    fobj.seek(0)
    for line in fobj:
        print(line.strip('\n'),)
