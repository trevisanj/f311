#!/usr/bin/env python

import argparse
import logging
import f311.pyfant as pf
import a99


a99.logging_level = logging.INFO
a99.flag_log_file = True


__doc__ = """PFANT Launcher -- Graphical Interface for Spectral Synthesis\n\nSingle and multi modes.\n\n
Multi mode
----------
"""+pf.gui._shared.DESCR_MULTI+\
"---------\n\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
     )
    args = parser.parse_args()

    app = a99.get_QApplication([])

    form0 = pf.XMulti()
    # this would start with "multi" tab selected form0.tabWidget.setCurrentIndex(3)

    rm = pf.RunnableManager()
    form1 = pf.XRunnableManager(form0, rm)
    form1.flag_close_mpl_plots_on_close = False
    form1.flag_close_message = False
    form0.set_manager_form(form1)
    # form1.show()
    # it is good to start the manager as late as possible, otherwise
    # the program will hang if, for example, the form fails to be created.
    rm.start()
    try:
        form0.show()
        app.exec_()
    finally:
        rm.exit()
