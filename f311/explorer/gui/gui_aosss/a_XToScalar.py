__all__ = ["XToScalar"]


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .a_XHelpDialog import *
import a99


_CLASS_PREFIX = ""
_CONFIG_OPERATIONS = "/gui/XToScalar/operations"


class XToScalar(XHelpDialog):
    """
    Edit Parameters to apply ToScalar blocks to a Spectrum List

    Relevant attributes:
      self.block: None or ToScalar instance, set before closing when one clicks on "OK"
      self.fieldname: string
    """

    def __init__(self, *args):
        from f311 import explorer as ex

        XHelpDialog.__init__(self, *args)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        self.previous_operations = ex.get_config().get_item(_CONFIG_OPERATIONS, [])
        self.block = None

        self.setWindowTitle("Extract Scalar")

        self.labelHelpTopics.setText("&Available operations")

        # self.help_data = collect_doc(blocks.sp2scalar, base_class=blocks.baseblocks.ToScalar)
        self.help_data = a99.collect_doc(ex.blocks.toscalar, base_class=ex.ToScalar)
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
        # ###
        # edit = self.editFunction = QLineEdit("ToScalar_SNR(0, 100000)")
        # label.setBuddy(edit)
        # self.grid.addWidget(label, 0, 0)
        # self.grid.addWidget(edit, 0, 1)
        label = keep_ref(QLabel(a99.enc_name_descr("&Target Field Name", "Leave blank to use Function Name")))
        label.setAlignment(Qt.AlignRight)
        edit = self.editFieldName = QLineEdit("")
        label.setBuddy(edit)
        self.grid.addWidget(label, 1, 0)
        self.grid.addWidget(edit, 1, 1)

        a99.place_center(self, 800, 600)


    def accept(self):
        from f311 import explorer as ex

        try:
            expr = str(self.cb_operation.currentText())
            symbols_available = a99.module_to_dict(ex.blocks.toscalar)
            import numpy as np
            symbols_available["np"] = np
            block = eval(expr.strip(), symbols_available)

            if not isinstance(block, ex.ToScalar):
                raise RuntimeError("Expression does not evaluate to a valid ToScalar Block")

            self.block = block
            fieldname = str(self.editFieldName.text()).strip()
            fieldname = a99.expr_to_fieldname(expr) if len(fieldname) == 0 else fieldname
            self.fieldname = a99.valid_fits_key(fieldname)

            # Saves new operation on close (if evaluated successfully)
            if not expr in self.previous_operations:
                self.previous_operations.append(expr)
                self.previous_operations.sort()
                ex.get_config().set_item(_CONFIG_OPERATIONS, self.previous_operations)

            return QDialog.accept(self)
        except Exception as e:
            self.add_log_error(a99.str_exc(e), True)
            return False
