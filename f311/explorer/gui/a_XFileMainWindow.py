from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
from matplotlib import pyplot as plt
import a99
from f311 import filetypes as ft
import f311


__all__ = ["XFileMainWindow", "NullEditor", "XFileMainWindowBase", "MyPage", "NullEditor"]


class MyPage(object):
    """Object holding data related to one tab in a XFileMainWindowBase object"""

    @property
    def flag_op(self):
        return not isinstance(self.editor, NullEditor)

    def __init__(self, text_tab="", flag_changed=False, text_saveas="Save as...",
                 text_load="Load...", cls_save=None, clss_load=(), wild="*.*", editor=None,
                 flag_autosave=False):
        if editor is None:
            editor = NullEditor()

        self.text_tab = text_tab
        self.text_saveas = text_saveas
        self.text_load = text_load
        # save class
        self.cls_save = cls_save
        # accepted load classes
        self.clss_load = clss_load
        # e.g. '*.fits'
        self.wild = wild
        # editor widgets
        self.editor = editor
        # True if the editor saves the file automatically ("(changed)" will never be shown)
        self.flag_autosave = flag_autosave

        self.flag_changed = flag_changed

    def make_text_load(self):
        t = self.text_load
        return t if t is not None else "Load {}...".format(self.cls_save.description)

    def make_text_saveas(self):
        t = self.text_saveas
        return t if t is not None else "Save {} as...".format(self.cls_save.description)


class XFileMainWindowBase(a99.XLogMainWindow):
    """Application template with file operations in two tabs: (application area) and (log)

    Args:
        parent: passed to QMainWindow constructor
        fobjs: sequence of DataFile objects to be loaded by their respective editors
    """

    def __init__(self, parent=None, fobjs=None):
        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        a99.XLogMainWindow.__init__(self, parent)

        self.save_dir = None
        self.load_dir = None

        # [MyPage, ...]
        self.pages = []

        # # Menu bar
        self.__add_menu()

        # # Central layout and widget
        #
        self.centralWidget = cw = QWidget()
        self.setCentralWidget(cw)

        self.centralLayout = lantanide = QVBoxLayout(cw)
        a99.set_margin(lantanide, 1)

        # ## Tabs
        tt = self.tabWidget = QTabWidget(self)
        lantanide.addWidget(tt)
        tt.setFont(a99.MONO_FONT)

        # ## "Last Log" label /  status label
        x = self.label_last_log = QLabel(self)
        # http://stackoverflow.com/questions/6721149/enable-qlabel-to-shrink-even-if-it-truncates-text
        x.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed))
        lantanide.addWidget(x)

        # Custom add stuff (for subclasses)
        self._add_stuff()

        # Adds tabs for pages
        for page in self.pages:
            self.tabWidget.addTab(page.editor, "")

        # Connects changed signals from all editor to keep track of changes
        for page in self.pages:
            page.editor.changed.connect(self._on_changed)

        a99.nerdify(self)

        self.load_many(fobjs)

        self._update_gui_text_tabs()

    def load_many(self, fobjs=None):
        """Loads as many files as the number of pages

        Args:
            fobjs: [filename or DataFile obj, ...]"""
        if fobjs is not None:
            # tolerance
            if not hasattr(fobjs, "__iter__"):
                fobjs = [fobjs]

            for index, (fobj, page) in enumerate(zip(fobjs, self.pages)):
                if fobj is None:
                    continue
                elif isinstance(fobj, ft.DataFile):
                    self.load(fobj, index)
                elif isinstance(fobj, str):
                    self.load_filename(fobj, index)
                else:
                    raise TypeError("Invalid object of class '{}'".format(fobj.__class__.__name__))

    def _add_stuff(self):
        """Responsible for adding menu options, widgets, and pages, setting window title etc.

        Not necessary to add widgets to the tabWidget
        """
        pass

    def __add_menu(self):
        b = self.menuBar()
        m = self.menu_file = b.addMenu("&File")
        ac = m.addAction(a99.get_icon("document-open"), "&Open...")
        ac.setShortcut("Ctrl+O")
        ac.triggered.connect(self.on_load)
        m.addSeparator()
        ac = m.addAction(a99.get_icon("document-save"), "&Save")
        ac.setShortcut("Ctrl+S")
        ac.triggered.connect(self.on_save)
        ac = m.addAction(a99.get_icon("document-save-as"), "Save &as...")
        ac.setShortcut("Ctrl+Shift+S")
        ac.triggered.connect(self.on_save_as)
        ac = m.addAction("Save a&ll...")
        ac.setShortcut("Alt+Shift+S")
        ac.triggered.connect(self.on_save_all)
        m.addSeparator()
        ac = m.addAction("Load &default")
        ac.setStatusTip("Loads default")
        ac.setShortcut("Ctrl+D")
        ac.triggered.connect(self.on_reset)
        m.addSeparator()
        ac = m.addAction(a99.get_icon("system-shutdown"), "&Quit")
        ac.setShortcut("Ctrl+Q")
        ac.triggered.connect(self.close)

    def _add_log_tab(self):
        """Adds element to pages and new tab"""

        # text_tab = "Log (Alt+&{})".format(len(self.pages)+1)
        text_tab = "Log"

        self.pages.append(MyPage(text_tab=text_tab))

        # ### Log tab
        te = self.textEdit_log = self.keep_ref(QTextEdit())
        te.setReadOnly(True)
        self.tabWidget.addTab(te, text_tab)


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Interface

    def load(self, fobj, index=None):
        """
        Loads given DataFile object. **tolerant with None**

        Args:
            fobj: object of one of accepted classes
            index: tab index to load fobj into. If not passed, loads into current tab
        """
        if index is None:
            index = self._get_tab_index()
        page = self.pages[index]

        if fobj is None:
            return


        if not isinstance(fobj, tuple(page.clss_load)):
            raise RuntimeError('Object to load must be in {0!s} (not a {1!s})'.format(
             [x.__name__ for x in page.clss_load], fobj.__class__.__name__))

        page.editor.load(fobj)
        self._update_gui_text_tabs()

    def load_filename(self, filename, index=None):
        """
        Loads file given filename

        Args:
            filename:
            index: tab index to load file into. If not passed, loads into current tab
        """
        filename = str(filename)  # QString protection
        if index is None:
            index = self._get_tab_index()
        page = self.pages[index]

        # Maybe this is set on purpose before loading attempt to leave new load_dir set (?)
        self.load_dir, _ = os.path.split(filename)

        clss = page.clss_load
        if len(clss) == 1:
            # If there is only one class to handle the file, will load it in a way that eventual
            # load errors will raise
            f = clss[0]()
            f.load(filename)
        else:
            # At the moment, the multi-class alternative will not display particular error information
            # if the file does not load
            f = f311.load_with_classes(filename, page.clss_load)
            if f is None:
                raise RuntimeError("Could not load '{0!s}'".format(filename))

        self.load(f, index)

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Qt override

    def closeEvent(self, event):
        flag_exit, ff = True, []
        for page in self.pages:
            ed = page.editor
            if ed and ed.f and page.flag_changed:
                ff.append(ed.f.description)

        if len(ff) > 0:
            s = "Unsaved changes\n  -" + ("\n  -".join(ff)) + "\n\nAre you sure you want to exit?"
            flag_exit = a99.are_you_sure(True, event, self, "Unsaved changes", s)
        if flag_exit:
            plt.close("all")

    def keyPressEvent(self, evt):
        """This handles Ctrl+PageUp, Ctrl+PageDown, Ctrl+Tab, Ctrl+Shift+Tab"""
        incr = 0
        if evt.modifiers() == Qt.ControlModifier:
            n = self.tabWidget.count()
            if evt.key() in [Qt.Key_PageUp, Qt.Key_Backtab]:
                incr = -1
            elif evt.key() in [Qt.Key_PageDown, Qt.Key_Tab]:
                incr = 1
            if incr != 0:
                new_index = self._get_tab_index() + incr
                if new_index < 0:
                    new_index = n - 1
                elif new_index >= n:
                    new_index = 0
                self.tabWidget.setCurrentIndex(new_index)


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Slots for Qt library signals

    # All file operations

    def on_load(self):
        try:
            if self._tab_is_op():
                self.__generic_load()
        except Exception as e:
            self.add_log_error(a99.str_exc(e), True, e)

    def on_save(self):
        try:
            if self._tab_is_op():
                self.__generic_save()
        except Exception as e:
            self.add_log_error(a99.str_exc(e), True, e)

    def on_save_as(self):
        try:
            if self._tab_is_op():
                self.__generic_save_as()
        except Exception as e:
            self.add_log_error(a99.str_exc(e), True, e)

    def on_save_all(self):
        index_save = self._get_tab_index()
        try:
            for index in range(self.tabWidget.count()):
                self.tabWidget.setCurrentIndex(index)
                try:
                    if not self.__generic_save():
                        # breaks if user cancels a "save as" operation
                        break
                except Exception as e:
                    self.add_log_error(a99.str_exc(e), True, e)
        finally:
            self.tabWidget.setCurrentIndex(index_save)

    def on_reset(self):
        if self._tab_is_op():
            editor = self._get_page().editor
            flag_ok = True
            if editor.f:
                descr = self._get_tab_description()
                r = QMessageBox.question(self, "Load default", "Current setup "
                                                               "for %s will be overwritten with a 'default' setup.\n\n"
                                                               "Confirm?" % descr, QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.Yes)
                flag_ok = r == QMessageBox.Yes
            if flag_ok:
                self._generic_reset()


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Gear


    def _on_changed(self):
        """Slot for changed events"""
        page = self._get_page()
        if not page.flag_autosave:
            page.flag_changed = True
            self._update_gui_text_tabs()

    def _get_tab_index(self):
        """Returns index of current selected tab."""
        return self.tabWidget.currentIndex()

    def _get_page(self):
        """Returns MyPage corresponding to current tab"""
        return self.pages[self._get_tab_index()]

    def _get_tab_description(self):
        """Returns "description" of current tab (tab text without shortcut info)."""
        text = self._get_page().text_tab
        if "(" in text:
            text = text[:text.index("(") - 1]
        text = text[0].lower() + text[1:]
        return text

    def _tab_is_op(self):
        return self._get_page().flag_op

    def _update_gui_text_tabs(self):
        """Iterates through pages to update tab texts"""
        for index, page in enumerate(self.pages):
            self.tabWidget.setTabText(index, "{} (Alt+&{}){}".format(page.text_tab, index+1, (" (changed)" if page.flag_changed else "")))

    def _generic_reset(self):
        page = self._get_page()
        # index = self._get_tab_index()
        # editor, text, cls = self.editors[index], self.text_loads[index], \
        #                     self.clss[index]
        fobj = page.cls_save()
        fobj.init_default()
        page.editor.load(fobj)
        # perhaps it is save to assume that the status is not 'changed' if there is a filename
        # assigned after init_default
        page.flag_changed = fobj.filename is None
        self._update_gui_text_tabs()

    def __generic_save(self):
        """Returns False if user has cancelled a "save as" operation, otherwise True."""
        page = self._get_page()
        f = page.editor.f
        if not f:
            return True
        if not page.editor.flag_valid:
            a99.show_error("Cannot save, {0!s} has error(s)!".format(f.description))
            return True
        if f.filename:
            f.save_as()

            self.add_log("Saved '{}'".format(f.filename))
            page.flag_changed = False
            self._update_gui_text_tabs()

            if hasattr(page.editor, "update_gui_label_fn"):
                page.editor.update_gui_label_fn()  # duck typing
            return True
        else:
            return self.__generic_save_as()

    def __generic_save_as(self):
        """Returns False if user has cancelled operation, otherwise True."""
        page = self._get_page()
        if not page.editor.f:
            return True
        if page.editor.f.filename:
            d = page.editor.f.filename
        else:
            d = os.path.join(self.save_dir if self.save_dir is not None \
                                 else self.load_dir if self.load_dir is not None \
                else ".", page.editor.f.default_filename)
        new_filename = QFileDialog.getSaveFileName(self, page.make_text_saveas(), d, page.wild)[0]
        if new_filename:
            self.save_dir, _ = os.path.split(str(new_filename))
            page.editor.f.save_as(str(new_filename))
            page.flag_changed = False
            self._update_gui_text_tabs()
            page.editor.update_gui_label_fn()
            return True
        return False

    def __generic_load(self):
        page = self._get_page()
        d = self.load_dir if self.load_dir is not None \
            else self.save_dir if self.save_dir is not None \
            else "."
        new_filename = QFileDialog.getOpenFileName(self, page.make_text_load(), d, page.wild+";;*.*")[0]
        if new_filename:
            self.load_filename(new_filename)


class NullEditor(object):
    """Class to fulfill requirement in XFileMainWindow, easiest way out, no bother"""
    f = None


class XFileMainWindow(XFileMainWindowBase):
    """Application template with file operations in two tabs: (application area) and (log)"""

    def __init__(self, *args, **kwargs):
        XFileMainWindowBase.__init__(self, *args, **kwargs)

        self._add_log_tab()
        # TODO make this flexible if needed
        if self.tabWidget.count() > 0:
            self.tabWidget.setCurrentIndex(0)
