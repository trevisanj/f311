__all__ = ["XHelpDialog"]


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99


class XHelpDialog(a99.XLogDialog):
    """
    Dialog with two areas: Fields Area and Help Area

    1. The Fields area contains a grid layout and the OK & Cancel buttons
    2. The Help Area contains a combo box and a text area

    Relevant attributes:
      self.help_data: [(class name without prefix, docstring), ...]
      self.block: None or ToScalar instance, set before closing when one clicks on "OK"
      self.grid: grid layout (initially empty)
      self.labelHelpTopics: label with text "Help Topics", exposed in case you want to change this text
      self.comboBox: combo box to add the help topics

    """

    def __init__(self, *args):
        a99.XLogDialog.__init__(self, *args)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        self.help_data = []

        # # Central layout
        lymain = self.layout_main = QVBoxLayout()
        a99.set_margin(lymain, 0)
        self.setLayout(lymain)

        # ## Title of Fields Area
        label = keep_ref(QLabel("<b>Setup</b>"))
        lymain.addWidget(label)

        # ## Fields Area
        wfields = QWidget()
        wfields.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lyfields = keep_ref(QHBoxLayout(wfields))
        lymain.addWidget(wfields)
        a99.set_margin(lyfields, 0)
        lyfields.setSpacing(2)

        # ### Left area of Fields Area
        lypanel = self.grid = QGridLayout()
        lyfields.addLayout(lypanel)


        # ### Right area of Fields Area (button box)
        bb = keep_ref(QDialogButtonBox())
        bb.setOrientation(Qt.Vertical)
        bb.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        lyfields.addWidget(bb)
        bb.rejected.connect(self.reject)
        bb.accepted.connect(self.accept)

        # ## Title of Help Area
        label = keep_ref(QLabel("<b>Help</b>"))
        lymain.addWidget(label)

        # ## Help Area

        # ### Panel containing a combobox to choose among help topics
        lypanel = QHBoxLayout()
        lymain.addLayout(lypanel)
        a99.set_margin(lypanel, 0)
        lypanel.setSpacing(2)
        ###
        label = self.labelHelpTopics = QLabel("Help Topics")
        lypanel.addWidget(self.labelHelpTopics)
        ###
        cb = self.comboBox = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_changed)
        lypanel.addWidget(cb)
        label.setBuddy(cb)
        ###
        lypanel.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # ### Text Edit below combobox
        x = self.textEdit = QTextEdit()
        x.setReadOnly(True)
        x.setStyleSheet("QTextEdit {color: %s}" % a99.COLOR_DESCR)
        lymain.addWidget(x)

    def combobox_changed(self):
        idx = self.comboBox.currentIndex()
        # self.textEdit.setText("<h1>%s</h1>%s\n" % (self.help_data[idx][0], self.help_data[idx][1].replace("\n", "<br>")))


        self.textEdit.setText("<h3>{}{}</h3><pre>{}</pre>\n".format(*self.help_data[idx]))


