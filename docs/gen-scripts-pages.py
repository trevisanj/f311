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

# These values must match those of the same variables in programs.py
SUBDIR = "autoscripts"
PREFIX_EDITABLE = "editable-"
PREFIX_AUTO = "leave-"

allinfo = f311.get_programs_dict(None, flag_protected=False)


def _get_help(script_name):
    """Runs script with "--help" options and grabs its output

    Source: https://stackoverflow.com/questions/4760215/running-shell-command-from-python-and-capturing-the-output
    """

    return subprocess.check_output([script_name, "--help"]).decode("utf8")


def main():
    for pkgname, infos in allinfo.items():
        print("\n".join(a99.format_box(pkgname)))
        for info in infos["exeinfo"]:
            print("Processing '{}'...".format(info.filename))

            nameonly = os.path.splitext(info.filename)[0]

            filename_auto = "{}{}.rst".format(PREFIX_AUTO, nameonly)
            path_editable = os.path.join("source", SUBDIR, "{}{}.rst".format(PREFIX_EDITABLE, nameonly))

            _doc = _get_help(info.filename)
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

if __name__ == "__main__":
    main()


