#!/usr/bin/env python

"""
Organizes simulation directory (creates folders, moves files, creates 'index.html')

  - moves 'root/report-*'       to 'root/reports'
  - moves 'root/C*'             to 'root/raw'
  - moves 'root/raw/simgroup*'  to 'root/'
  - moves 'root/raw/report-*'   to 'root/reports'
  - moves 'root/raw/group*.splist'   to 'root'
  - [re]creates 'root/reports/index.html'

This script can be run from one of these directories:
  - 'root' -- a directory containing at least one of these directories: 'reports', 'raw'
  - 'root/raw'
  - 'root/reports'

The script will use some rules to try to figure out where it is running from
"""

import argparse
import os
import glob
import sys
import f311.aosss as ao
import logging
import a99


a99.logging_level = logging.INFO
a99.flag_log_file = True


class MoveTask(object):
    def __init__(self, source, dest):
        self.source = source
        self.dest = dest

    def __str__(self):
        cwd = os.getcwd()
        return "Move '{}' to '{}'".format(os.path.relpath(self.source, cwd),
                                          os.path.relpath(self.dest, cwd))

    def run(self):
        cwd = os.getcwd()
        dest_dir, _ = os.path.split(self.dest)
        if not os.path.exists(dest_dir):
            a99.get_python_logger().info("Creating directory '%s'..." % dest_dir)
            os.makedirs(dest_dir)
        a99.get_python_logger().info("Moving '{}' to '{}'".format(os.path.relpath(self.source, cwd),
                                                               os.path.relpath(self.dest, cwd)))
        os.rename(self.source, self.dest)


if __name__ == "__main__":
    lggr = a99.get_python_logger()

    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
    )

    args = parser.parse_args()

    # Tries to figure out where the root directory is
    rules = (
    ("reports", "."),
    ("raw", "."),
    ("../reports", ".."),
    ("../raw", ".."),
    )
    root = None
    for _dir, _root in rules:
        if os.path.isdir(_dir):
            root = _root
            lggr.info("Root directory is found to be '{}' because found directory '{}'".format(_root, _dir))
            break
    if root is None:
        if len(glob.glob("C*.fits")) > 0:
            lggr.info("Root directory is found to be '.' because found files 'C*.fits'")
            root = "."
        else:
            lggr.critical("Cannot determine simulations root directory, sorry")
            sys.exit()

    move_specs = (
    ('./report-*', './reports'),
    ('./C*', './raw'),
    ('./raw/simgroup-*', './'),
    ('./raw/report-*', './reports'),
    ('./raw/group*.splist', './'),
    )

    # Assembles a list of files to be moved
    to_move = []
    flag_reports = False
    for a, b in move_specs:
        files = glob.glob(os.path.join(root, a))
        for file in files:
            flag_reports = flag_reports or 'report-' in file
            full = os.path.abspath(file)
            if os.path.isfile(full):
                to_move.append(MoveTask(full,
                                        os.path.abspath(os.path.join(root, b, os.path.basename(file)))))

    # Determines whether there are reports to create index
    index_html = os.path.relpath(os.path.join(root, "reports", "index.html"))
    flag_reports = flag_reports or len(glob.glob(os.path.join(root, "reports", "report-*.html"))) > 0

    for task in to_move:
        lggr.info(task)

    lggr.info('Tasks Summary:')
    lggr.info(('  - Move {} object{}'.format(len(to_move), "s" if len(to_move) != 1 else "")))
    if flag_reports:
        lggr.info("  - Create '{}'".format(index_html))
    else:
        lggr.info("  - Will not create '{}' (no reports found)".format(index_html))

    if len(to_move) == 0 and not flag_reports:
        lggr.info('Nothing to do')
        sys.exit()

    flag_continue = False
    msg = "Continue (Y/n)? "
    while True:
        yn = input(msg)
        if yn == "":
            yn = "Y"
        if yn.upper() == "Y":
            flag_continue = True
            break
        elif yn.upper() == "N":
            break
        msg = "Please answer 'y' or 'n': "


    if not flag_continue:
        sys.exit()

    for task in to_move:
        task.run()

    if flag_reports:
        lggr.info("Creating '{0}'...".format(index_html))
        ao.create_index(os.path.join(root, "reports"))






