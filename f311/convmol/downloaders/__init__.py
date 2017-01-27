import a99
import logging

# Tests importing packages robobrowser and bs4, requirements for downloaders
flag_ok = True
try:
    from robobrowser import RoboBrowser
    del RoboBrowser
except ImportError as e:
    flag_ok = False
    logging.warning("failed to import package robobrowser.Robobrowser: '{}', "
                    "f311.filetypes.downloaders will not be available".format(a99.str_exc(e)))

if flag_ok:
    try:
        import bs4
        del bs4
    except ImportError as e:
        flag_ok = False
        logging.warning("failed to import package bs4 (Beautiful Soup 4): '{}', "
                        "f311.filetypes.downloaders will not be available".format(a99.str_exc(e)))

del a99, logging

if flag_ok:
    from .downhitran import *
    from .downnist import *
