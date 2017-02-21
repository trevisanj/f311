__all__ = ["XUseSpectrumBlock"]


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .a_XHelpDialog import *
import a99


_CONFIG_OPERATIONS = "/gui/XUseSpectrumBlock/operations"


class XUseSpectrumBlock(XHelpDialog):
    """
    Edit Parameters to apply a SpectrumBlock to each spectrum in a Spectrum List

    Relevant attributes (set on close):
      self.block: None or SpectrumBlock instance
    """

    def __init__(self, *args):
        from f311 import explorer as ex

        XHelpDialog.__init__(self, *args)

        self.previous_operations = ex.get_config().get_item(_CONFIG_OPERATIONS, [])
        self.block = None

        self.setWindowTitle("Transform")

        self.labelHelpTopics.setText("&Available operations")

        self.help_data = a99.collect_doc(ex.sb, base_class=ex.SpectrumBlock)
        self.comboBox.addItems([x[0] for x in self.help_data])
        ###
        label = QLabel(a99.enc_name_descr("O&peration", "See help below"))
        label.setAlignment(Qt.AlignRight)
        cb = self.cb_operation = QComboBox()
        label.setBuddy(cb)
        cb.setEditable(True)
        cb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cb.addItems(self.previous_operations)
        self.grid.addWidget(label, 0, 0)
        self.grid.addWidget(cb, 0, 1)

        a99.place_center(self, 800, 600)


    def accept(self):
        from f311 import explorer as ex

        try:
            expr = str(self.cb_operation.currentText())
            block = eval(expr.strip(), {}, a99.module_to_dict(ex.blocks.sb))

            if not isinstance(block, ex.SpectrumBlock):
                raise RuntimeError("Expression does not evaluate to a valid Spectrum Block")

            self.block = block

            # Saves new operation on close (if evaluated successfully)
            if not expr in self.previous_operations:
                self.previous_operations.append(expr)
                self.previous_operations.sort()
                ex.get_config().set_item(_CONFIG_OPERATIONS, self.previous_operations)

            return QDialog.accept(self)
        except Exception as e:
            self.add_log_error(a99.str_exc(e), True)
            return False
