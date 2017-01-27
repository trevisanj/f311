#!/usr/bin/env python3

"""
Lists all programs available
"""

import a99
import argparse
import os
from collections import OrderedDict
import f311.explorer as ex

def _get_programs_list(format, pkgname_only=None):

    allinfo = OrderedDict()
    pkgnames = []
    for pkgname, pkg in ex.collaborators().items():
        if pkgname_only is not None and pkgname != pkgname_only:
                continue
        allinfo["Package '{}'".format(pkgname)] = a99.get_exe_info(a99.get_scripts_path(module=pkg))
        pkgnames.append(pkgname)

    # This can be called (without much shame) a "gambiarra"
    if "ftpyfant" in pkgnames:
        import f311.pyfant as pf
        allinfo["PFANT Fortran binaries"] = pf.get_fortrans()

    ret = format_programs(allinfo, format)

    return ret


def format_programs(allinfo, format):
    ret = []
    # will indent listing only if there is more than 1 package listed
    ind = 1 if len(allinfo) > 1 else 0
    for title, exeinfo in allinfo.items():
        if len(exeinfo) == 0:
            continue

        ret.extend(a99.format_h1(title, format) + [""])
        linesp, module_len = a99.format_exe_info(exeinfo, format, ind)
        ret.extend(linesp)

    return ret



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('format', type=str, help='Print format', nargs="?", default="text",
                        choices=["text", "markdown-list", "markdown-table"])
    parser.add_argument('--pkgname', type=str, help='Package name', default="(all)")
    args = parser.parse_args()

    pkgname_only = args.pkgname if args.pkgname is not "(all)" else None

    print("\n".join(_get_programs_list(args.format, pkgname_only)))

