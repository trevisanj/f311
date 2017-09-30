from PyQt5.QtWidgets import *
from .a_XFileMainWindowBase import *

__all__ = ["XFileMainWindow", "NullEditor"]

class XFileMainWindow(XFileMainWindowBase):
    """Application template with file operations in two tabs: (application area) and (log)"""

    def __init__(self, *args, **kwargs):
        XFileMainWindowBase.__init__(self, *args, **kwargs)

        self._add_log_tab()
        # TODO make this flexible if needed
        self.tabWidget.setCurrentIndex(0)

    def _add_stuff(self):
        # ### Custom Area tab will have a widget **without** a layout, named "gotting"
        w0 = self.gotting = QWidget()
        self.tabWidget.addTab(w0, "")
