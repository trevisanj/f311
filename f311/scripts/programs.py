#!/usr/bin/env python

"""
Lists all programs available
"""

import argparse
import os
from collections import OrderedDict
import glob
import sys
import a99
import f311
import re

# These values must match those of the same variables in <project-root>/docs/gen-script-pages.py
SUBDIR = "autoscripts"
PREFIX_EDITABLE = "script-"


def _add_PFANT(d):
    # This can be called (without much shame) a "gambiarra"
    import pyfant as pf
    d["PFANT"] = {"description": "Spectral synthesis-related Fortran binaries",
                  "exeinfo": pf.get_fortrans()}

def _get_programs_dict(pkgname_only, flag_protected, flag_no_pfant=False):
    """Returns dictionary {(package description): [ExeInfo0, ...], ...}"""

    allinfo = f311.get_programs_dict(pkgname_only, flag_protected)
    if not flag_no_pfant and "pyfant" in allinfo:
        _add_PFANT(allinfo)
    return allinfo


def _format_programs_dict(allinfo, format):
    ret = []
    # will indent listing only if there is more than 1 package listed
    ind = 1 if len(allinfo) > 1 else 0
    for name, dexeinfo in allinfo.items():
        descr = dexeinfo["description"]
        exeinfo = dexeinfo["exeinfo"]
        if len(exeinfo) == 0:
            continue

        title = "{} -- {}".format(name, descr)

        # **Note** Using h3/h4 because ot ReST context of use, but it is possible to change this
        ret.extend(a99.format_h3(title, format) + [""])
        linesp, module_len = a99.format_exe_info(exeinfo, format, ind)
        ret.extend(linesp)

    return ret


def _list_packages():
    print("\n".join(a99.format_h1("List of packages available")))
    print("\n".join(f311.COLLABORATORS_S))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,  formatter_class=a99.SmartFormatter)
    parser.add_argument('format', type=str, help='Print format', nargs="?", default="text",
                        choices=["text", "markdown-list", "markdown-table", "rest-list", "rest-toctree"])
    parser.add_argument('-p', '--pkgname', type=str, help='List programs from this package only', default="(all)")
    parser.add_argument('-l', '--list-packages', action="store_true", help='Lists all packages')
    parser.add_argument('-k', '--rest-links', action="store_true",
     help='If format=="rest-list", '
          'renders program names as links to their respective documentation pages')
    parser.add_argument('-n', '--no-pfant', action="store_true",
     help='Does not list PFANT binaries')
    parser.add_argument('-_', '--protected', action="store_true", help="Includes protected scripts (starting with '_')")
    args = parser.parse_args()

    pkgname_only = args.pkgname if args.pkgname is not "(all)" else None

    if args.list_packages:
        _list_packages()
        sys.exit()

    if pkgname_only is not None:
        if pkgname_only not in f311.COLLABORATORS_S:
            print("Invalid package name: '{}'\n\n".format(pkgname_only))
            _list_packages()
            sys.exit()

    allinfo = _get_programs_dict(pkgname_only, args.protected, args.no_pfant)
    strlist = _format_programs_dict(allinfo, args.format)


    _out = "\n".join(strlist)

    if args.format.startswith("rest") and args.rest_links:
        out = re.sub("\* ``(.*)\.py``",
                     lambda match: "* :doc:`{0}.py <{1}/{2}{0}>`".format(match.group(1), SUBDIR, PREFIX_EDITABLE),
                     _out)
    else:
        out = _out

    print(out)
