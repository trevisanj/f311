"""Widget to edit a MargAbondsFwhm object."""


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import types
import traceback
import a99
import f311.filetypes as ft


__all__ = ["WFileAbXFwhm"]


class WFileAbXFwhm(QWidget):
    """
    Editor for editor widget.

    Args:
      parent=None
    """

    # Emitted whenever any value changes
    changed = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # # Setup & accessible attributes

        # Whether all the values in the fields are valid or not
        self.flag_valid = False  # initialized to False because not loaded yet
        self.f = None  # FileOptions object
        self.logger = a99.get_python_logger()
        # FileAbonds instance to check for existence of atomic symbols
        self.file_abonds = None


        # # Internal stuff that must not be accessed from outside

        # options map: list of _Option
        self.omap = []
        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False

        # # Central layout

        la = self.layout_main = QVBoxLayout()
        a99.set_margin(la, 0)
        self.setLayout(la)

        # ## Splitter with scroll area and descripton+error area
        sp = self.splitter = QSplitter(Qt.Vertical)
        la.addWidget(sp)

        # ### Text edit

        # ### Editor for multi setup
        editor = self.editor = QPlainTextEdit()
        # editor.setStyleSheet("QPlainTextEdit {background-color: #000000}")
        # editor.textChanged.connect(self.on_edited)
        editor.modificationChanged.connect(self.on_edited)
        sp.addWidget(editor)
        self.highlight = a99.PythonHighlighter(editor.document())


        # ### Second widget of splitter
        # layout containing description area and a error label
        wlu = QWidget()
        lu = QVBoxLayout(wlu)
        a99.set_margin(lu, 0)
        lu.setSpacing(4)
        x = self.textEditInfo = QTextEdit(self)
        x.setReadOnly(True)
        x.setStyleSheet("QTextEdit {color: %s}" % a99.COLOR_DESCR)
        lu.addWidget(x)
        sp.addWidget(wlu)

        # ### Adjust splitter proportion
        sp.setStretchFactor(0, 8)
        sp.setStretchFactor(1, 2)

        self.setEnabled(False)  # disabled until load() is called
        a99.style_checkboxes(self)
        self.flag_process_changes = True

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def load(self, x):
        assert isinstance(x, ft.FileAbXFwhm)
        self.f = x
        self.__update_from_data()
        # this is called to perform file validation upon loading
        self.validate()
        
        self.setEnabled(True)

    def validate(self):
        """Forces validation of text in editor."""
        if self.f:
            self.__update_data()
        else:
            self.flag_valid = False

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        pass  # self.editor.setFocus()

#    def eventFilter(self, obj_focused, event):
#        pass
#        return False

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def on_edited(self):
        # http://stackoverflow.com/questions/22685463/qt5-tell-qplaintextedit-to-ignore-syntax-highlighting-changes
        if not self.flag_process_changes:
            return
        self.editor.document().setModified(False)
        self.__update_data()
        self.changed.emit()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear

    def __validate(self):
        f = ft.FileAbXFwhm()
        # first validation: code parses OK and has "ab" and "conv" variables
        f.source = str(self.editor.toPlainText())
        f.validate(self.file_abonds)

    def __update_from_data(self):
        self.flag_process_changes = False
        try:
            self.editor.setPlainText(self.f.source)
        finally:
            self.flag_process_changes = True

    def __update_data(self):
        emsg, flag_error = "", False
        try:
            self.__validate()
            self.f.source = str(self.editor.toPlainText())

        except:
            flag_error = True
            etype, value, _ = sys.exc_info()
            emsg = "<b>Error</b><br><pre>"+\
                   ("".join(_format_exception_only(etype, value)))+"</pre>"
            # ShowError(str(E))
        self.flag_valid = not flag_error
        self.__set_descr_text('<span style="color: %s">%s</div>' % (a99.COLOR_ERROR, emsg))

    def __set_descr_text(self, x):
        """Sets text of labelDescr."""
        self.textEditInfo.setText(x)


def _format_exception_only(etype, value):
    """[Copied from the traceback module] Format the exception part of a traceback.

    [Copied from the traceback module and changed to ignore filename]

    The arguments are the exception type and value such as given by
    sys.last_type and sys.last_value. The return value is a list of
    strings, each ending in a newline.

    Normally, the list contains a single string; however, for
    SyntaxError exceptions, it contains several lines that (when
    printed) display detailed information about where the syntax
    error occurred.

    The message indicating which exception occurred is always the last
    string in the list.

    """

    # An instance should not have a meaningful value parameter, but
    # sometimes does, particularly for string exceptions, such as
    # >>> raise string1, string2  # deprecated
    #
    # Clear these out first because issubtype(string1, SyntaxError)
    # would raise another exception and mask the original problem.
    if (isinstance(etype, BaseException) or
        isinstance(etype, object) or
        etype is None or type(etype) is str):
        return [traceback._format_final_exc_line(etype, value)]

    stype = etype.__name__

    if not issubclass(etype, SyntaxError):
        return [_format_final_exc_line(stype, value)]

    # It was a syntax error; show exactly where the problem was found.
    lines = []
    try:
        msg, (filename, lineno, offset, badline) = value.args
    except Exception:
        pass
    else:
        lines.append('Line %d\n' % lineno)
        if badline is not None:
            lines.append('    %s\n' % badline.strip())
            if offset is not None:
                caretspace = badline.rstrip('\n')
                offset = min(len(caretspace), offset) - 1
                caretspace = caretspace[:offset].lstrip()
                # non-space whitespace (likes tabs) must be kept for alignment
                caretspace = ((c.isspace() and c or ' ') for c in caretspace)
                lines.append('    %s^\n' % ''.join(caretspace))
        value = msg

    lines.append(traceback._format_final_exc_line(stype, value))
    return lines


def _format_final_exc_line(etype, value):
    """[Copied from traceback module] Return a list of a single line -- normal case for format_exception_only.

    [Changed to ignore the exception type]"""
    valuestr = traceback._some_str(value)
    if value is None or not valuestr:
        line = "%s\n" % etype
    else:
        line = "%s\n" % valuestr
    return line
