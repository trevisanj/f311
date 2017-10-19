import a99
import os
import shutil
import glob

if a99.yesno("Delete everything, except .py files", True):
    for f in glob.glob("*"):
        if f.endswith(".py"):
            print("Skipping '{}'".format(f))
        else:
            if os.path.isdir(f):
                print("Deleting tree '{}'...".format(f))
                shutil.rmtree(f)
            else:
                print("Deleting file '{}'...".format(f))
                os.unlink(f)
