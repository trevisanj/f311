"""Graphicsl interface for PFANT"""

__all__ = ["XPFANT"]

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os.path
import copy
import shutil
import a99
import f311.explorer as ex
import f311.filetypes as ft



################################################################################
class XPFANT(ex.XMainAbonds):
    """
    Args:
      parent=None: nevermind
      file_main (optional)-- FileMain instance
    """

    def __init__(self, *args, **kwargs):
        ## State variables
        ex.XMainAbonds.__init__(self, *args, **kwargs)

        # # Central layout

        # ## Main control bar

        l = self.controlLayout
        w = self.buttonSubmit = QPushButton("&Submit job")
        w.clicked.connect(self.on_submit)
        l.addWidget(w)
        w = self.checkbox_custom_id = QCheckBox("Custom session directory")
        w.stateChanged.connect(self.on_checkbox_custom_id_state_changed)
        l.addWidget(w)
        w = self.lineEdit_custom_id = QLineEdit()
        w.setFixedWidth(100)
        l.addWidget(w)
        # s = self.spacer0 = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        l.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # # Final adjustments
        self.setWindowTitle("PFANT launcher")
        self.__update_lineEdit_custom_id()


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # "Duck-typing"

    def set_manager_form(self, x):
        from f311 import pyfant as pf
        assert isinstance(x, pf.XRunnableManager)
        self._manager_form = x
        self._rm = x.rm

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Slots for Qt library signals

    def on_submit(self):
        from f311 import pyfant as pf
        flag_ok = True
        errors = self._check_single_setup()
        if len(errors) == 0:
            # more error checking
            if self.checkbox_custom_id.isChecked():
                s = self.__get_custom_session_id()
                if len(s) == 0:
                    errors.append("Please inform custom session id.")
                elif len(errors) == 0: # will only offer to remove directory if everything is ok so far
                    dirname = _get_custom_dirname(s)
                    if os.path.isdir(dirname):
                        r = QMessageBox.question(self, "Directory exists",
                         "Directory '%s' already exists.\n\n"
                         "Would you like to remove it?" % dirname,
                         QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
                        if r == QMessageBox.Yes:
                            try:
                                shutil.rmtree(dirname)
                            except Exception as e:
                                errors.append(str(e))
                        else:
                            return

        if len(errors) == 0:
            try:
                self._manager_form.show()
                self._manager_form.raise_()
                self._manager_form.activateWindow()
                self.__submit_job()
            except Exception as e:
                errors.append(str(e))
                a99.get_python_logger().exception("Cannot submit job")
        if len(errors) > 0:
            a99.show_error("Cannot submit job:\n  - "+("\n  - ".join(errors)))

    def on_checkbox_custom_id_state_changed(self):
        self.__update_lineEdit_custom_id()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Slots for signals emited by ftpyfant widgets


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Internals

    def __get_custom_session_id(self):
        return str(self.lineEdit_custom_id.text()).strip()

    def __submit_job(self):
        from f311 import pyfant as pf
        r = pf.Combo()
        if self.checkbox_custom_id.isChecked():
            custom_id = self.__get_custom_session_id()
            r.conf.sid.id = custom_id
            if _get_custom_dirname(custom_id) == custom_id:
                # Understands that session dirname prefix must be cleared
                r.sid.id_maker.session_prefix_singular = ""

        r.conf.opt = copy.copy(self.oe.f)
        r.conf.file_main = self.me.f
        r.conf.file_abonds = self.ae.f
        r.conf.file_dissoc = self.ae.f.get_file_dissoc()
        r.conf.flag_output_to_dir = True
        self._rm.add_runnables([r])

    def __update_lineEdit_custom_id(self):
        self.lineEdit_custom_id.setEnabled(self.checkbox_custom_id.isChecked())


# This sector defines how custom directory name is made up

def _get_custom_dirname(session_id):
    from f311 import pyfant as pf
    # return pf.SESSION_PREFIX_SINGULAR+session_id
    return session_id