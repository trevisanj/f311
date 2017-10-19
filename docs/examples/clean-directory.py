#!/usr/bin/env python

import a99
import os

if a99.yesno("Delete everything from all subdirectories, except .py files", True):
    for dirname, dirnames, filenames in os.walk(".", False):
        for filename in filenames:
            deleted_all = True
            if not (filename.startswith(".") or filename.endswith(".py")):
                target = os.path.join(dirname, filename)
                print("Deleting file '{}'...".format(target))
                os.unlink(target)
            else:
                deleted_all = False

        if len(dirnames) == 0 and deleted_all:
            print("Removing directory '{}'...".format(dirname))
            os.rmdir(dirname)
