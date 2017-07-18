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


def _get_subpackage_names():
    """Figures out the names of the subpackages of f311

    Source: http://stackoverflow.com/questions/832004/python-finding-all-packages-inside-a-package
    """

    dir_ = os.path.dirname(f311.__file__)

    def is_package(d):
        d = os.path.join(dir_, d)
        return os.path.isdir(d) and glob.glob(os.path.join(d, '__init__.py*'))

    ret = list(filter(is_package, os.listdir(dir_)))
    ret.sort()
    return ret


def _get_scripts_path(pkgname):
    """Returns full path to scripts directory, assuming it is like .../f311/<pkgname>/scripts"""
    return os.path.join(os.path.dirname(f311.__file__), pkgname, "scripts")


def _get_programs_dict(pkgname_only, flag_protected):
    """Returns dictionary {(package description): [ExeInfo0, ...], ...}"""

    allinfo = OrderedDict()
    pkgnames = []
    for pkgname in _get_subpackage_names():
        if pkgname_only is not None and pkgname != pkgname_only:
                continue
        allinfo["Package '{}'".format(pkgname)] = a99.get_exe_info(_get_scripts_path(pkgname), flag_protected)
        pkgnames.append(pkgname)

    # This can be called (without much shame) a "gambiarra"
    if "pyfant" in pkgnames:
        import f311.pyfant as pf
        allinfo["PFANT Fortran binaries"] = pf.get_fortrans()

    return allinfo


def _format_programs_dict(allinfo, format):
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
                        choices=["text", "markdown-list", "markdown-table", "rest-list"])
    parser.add_argument('-p', '--pkgname', type=str, help='List programs from this package only', default="(all)")
    parser.add_argument('-l', '--list-packages', action="store_true", help='Lists all sub-packages of f311')
    parser.add_argument('-_', '--protected', action="store_true", help="Includes protected scripts (starting with '_')_")
    args = parser.parse_args()

    if args.list_packages:
        print("\n".join(a99.format_h1("Sub-packages of f311")))
        print("\n".join(_get_subpackage_names()))
        sys.exit()

    pkgname_only = args.pkgname if args.pkgname is not "(all)" else None



    allinfo = _get_programs_dict(pkgname_only, args.protected)
    strlist = _format_programs_dict(allinfo, args.format)
    print("\n".join(strlist))
    print("http://github.com/trevisanj/f311\n")

