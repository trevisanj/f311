#!/usr/bin/env python

"""Script to generate .rst pages for each script in the f311 package

For each script, two .rst files are generated: one that can be edited later, and one that must not
be edited because it will be overwritten every time this script is run.
"""

import f311
import os
import a99
import subprocess
import sys
import argparse


# These values must match those of the same variables in programs.py
SUBDIR = "autoscripts"
PREFIX_EDITABLE = "script-"
PREFIX_AUTO = "leave-"


def _get_help(script_name):
    """Runs script with "--help" options and grabs its output

    Source: https://stackoverflow.com/questions/4760215/running-shell-command-from-python-and-capturing-the-output
    """

    return subprocess.check_output([script_name, "--help"]).decode("utf8")


def main(allinfo, flag_page_only=False):


    # Page to be saves as "scripts.rst"
    index_page = [
"Index of applications (scripts)",
"===============================",
"",
".. toctree::",
"    :maxdepth: 1",
"",
]

    for pkgname, infos in allinfo.items():
        if pkgname in ("ariastro", "convmolworks"):
            continue

        print("\n".join(a99.format_box(pkgname)))
        for info in infos["exeinfo"]:
            print("Processing '{}'...".format(info.filename))

            nameonly = os.path.splitext(info.filename)[0]

#            page.append("    {} <autoscripts/{}{}>".format(info.description, PREFIX_EDITABLE, nameonly))
            index_page.append("    autoscripts/{}{}".format(PREFIX_EDITABLE, nameonly))

            if flag_page_only:
                continue

            filename_auto = "{}{}.rst".format(PREFIX_AUTO, nameonly)
            path_editable = os.path.join("source", SUBDIR, "{}{}.rst".format(PREFIX_EDITABLE, nameonly))

            try:
                _doc = _get_help(info.filename)
            except subprocess.CalledProcessError:
                print("***FAILED***")
                continue

            doc = "\n".join(["    "+x for x in _doc.split("\n")])
            title = "Script ``{}``".format(info.filename)
            dash = "="*len(title)

            # Creates the editable file only if it does not exist
            if not os.path.exists(path_editable):
                page_editable = "{}\n{}\n\n.. include:: {}".format(
                    title,
                    dash,
                    filename_auto)

                with open(path_editable, "w") as file:
                    file.write(page_editable)

                print("Wrote file '{}'".format(path_editable))


            # The other file is always created/overwritten
            page_auto = ".. code-block:: none\n\n{}\n\nThis script belongs to package *{}*\n".format(
                doc,
                pkgname
            )
            path_auto = os.path.join("source", SUBDIR, filename_auto)
            with open(path_auto, "w") as file:
                file.write(page_auto)

            print("Wrote file '{}'".format(path_auto))

    path_index = os.path.join("source", "scripts.rst")
    with open(path_index, "w") as file:
        file.write("\n".join(index_page))
    print("\n\n\n")
    print("Wrote scripts index file '{}'".format(path_index))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,  formatter_class=a99.SmartFormatter)
    parser.add_argument('-i', '--index-only', action="store_true", help='Generates scripts index page only (source/scripts.rst)')

    args = parser.parse_args()

    allinfo = f311.get_programs_dict(None, flag_protected=False)
    main(allinfo, args.index_only)


