__all__ = ["XGroupSpectra"]


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .a_XHelpDialog import *
import a99


class XGroupSpectra(XHelpDialog):
    """
    Edit Parameters gb.py a SpectrumList

    Relevant attributes (set on close):
      self.block: None or GroupBlock instance
      self.group_by: sequence of
          (field names) = (FITS header keys) = (keys in Spectrum.more_headers)
    """

    def __init__(self, *args):
        from f311 import explorer as ex

        XHelpDialog.__init__(self, *args)

        self.block = None
        self.group_by = None


        self.setWindowTitle("Group Spectra")

        self.labelHelpTopics.setText("&Available operations")

        self.help_data = a99.collect_doc(ex.blocks.gb, base_class=ex.GroupBlock)
        self.comboBox.addItems([x[0] for x in self.help_data])
        ###
        label = QLabel(a99.enc_name_descr("O&peration", "See help below"))
        edit = self.editFunction = QLineEdit("GB_UseNumPyFunc(np.mean)")
        label.setBuddy(edit)
        self.grid.addWidget(label, 0, 0)
        self.grid.addWidget(edit, 0, 1)
        ###
        label = QLabel(a99.enc_name_descr("&Group fieldnames", "Comma-separated without quotes"))
        edit = self.editGroupBy = QLineEdit("")
        label.setBuddy(edit)
        self.grid.addWidget(label, 1, 0)
        self.grid.addWidget(edit, 1, 1)

        a99.place_center(self, 800, 600)

    def accept(self):
        from f311 import explorer as ex

        try:
            expr = str(self.editFunction.text())
            symbols_available = a99.module_to_dict(ex.blocks.gb)
            import numpy
            symbols_available["np"] = numpy
            block = eval(expr.strip(), {}, symbols_available)

            if not isinstance(block, ex.GroupBlock):
                raise RuntimeError("Expression does not evaluate to a valid Grouping Block")

            s_group_by = str(self.editGroupBy.text())
            group_by = [str(y).upper() for y in [x.strip() for x in s_group_by.split(",")] if len(y) > 0]

            self.block = block
            self.group_by = group_by

            return QDialog.accept(self)
        except Exception as e:
            self.add_log_error(a99.str_exc(e), True)
            return False

