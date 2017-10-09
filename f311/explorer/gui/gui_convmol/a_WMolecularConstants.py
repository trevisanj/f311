from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
from .a_WDBState import WDBState
import copy
import f311.filetypes as ft
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
from .a_WDBState import WDBState
import copy
import f311.filetypes as ft


__all__ = ["WMolecularConstants"]

# Spacing for grid layouts
_LAYSP_GRID = 4
# Margin for grid layouts
_LAYMN_GRID = 0
_SPACE_BETWEEN_FIELDS = 8
# Spacing between label and combobox
_LAYSP_CB = 3
# Spacing for vertical layouts
_LAYSP_V = 10
# Margin for vertical layouts ((caption, combobox); grid)
_LAYMN_V = 6
# Spacing for main layout
_LAYSP_MAIN = 6
# Margin for main layout
_LAYMN_MAIN = 0
# Spacing for toolbar
_LAYSP_TOOLBAR = 8
# Margin for toolbar
_LAYMN_TOOLBAR = 2
# Spacing for frames that are inside frames
_LAYSP_FRAME1 = 6
# Margin for frames inside frames
_LAYMN_FRAME1 = 0



################################################################################
class _XHLF(a99.XLogMainWindow):
    """
    Window to show Hönl-London factors for given MolConsts object
    Args:
      parent=None: nevermind
      text: string
    """

    def __init__(self, parent, moldb, molconsts, fcfs):
        a99.XLogMainWindow.__init__(self, parent)

        self.moldb = moldb
        self.molconsts = molconsts
        self.fcfs = fcfs

        cw = self.centralWidget = QWidget()
        self.setCentralWidget(cw)


        # # Vertical layout: toolbar and text are stacked

        lv = self.layout_main = QVBoxLayout(cw)

        # ## Horizontal layout: toolbar

        lh = self.layout_molecule = QHBoxLayout()
        lv.addLayout(lh)

        ###
        la = self.keep_ref(QLabel("Multiply by Franck-Condon Factors"))
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        lh.addWidget(la)
        ###
        cb = self.checkbox_fcf = QCheckBox()
        lh.addWidget(cb)

        ###
        b = self.keep_ref(QPushButton("&Calculate"))
        lh.addWidget(b)
        b.clicked.connect(self._calculate)
        ###
        lh.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        ###

        # ## Text area

        cw = self.textEdit = QPlainTextEdit()
        lv.addWidget(cw)
        cw.setReadOnly(True)  # allows copy but not editing
        cw.setFont(a99.MONO_FONT)

        self.setWindowTitle("Hönl-London factors")
        self.setGeometry(0, 0, 800, 600)
        a99.place_center(self)
        a99.nerdify(self)

    def _calculate(self):

        flag_fcf = self.checkbox_fcf.isChecked()

        if flag_fcf:
            if self.fcfs is None or len(self.fcfs) == 0:
                self.add_log_error("FCFs not available", True)

        try:
            import f311.explorer as ex
            import f311.physics as ph
            import f311.convmol as cm
            import tabulate

            l_text = []

            self.status("Calculating...")
            molconsts = copy.deepcopy(self.molconsts)
            molconsts.None_to_zero()
            for vl in range(10):
                for v2l in range(10):
                    l_text.extend(a99.format_box("vl, v2l = ({}, {})".format(vl, v2l)))

                    factor = 1.
                    if flag_fcf:
                        try:
                            factor = self.fcfs[(vl, v2l)]
                        except KeyError:
                            l_text.append("Franck-Condon Factor not available")
                            continue

                    rows, header = [], None
                    for J in range(40):
                        mtools = ph.multiplicity_toolbox(molconsts, flag_normalize=True)
                        mtools.populate(vl, v2l, J)

                        if header is None:
                            branches = [key[3] for key in mtools.dict_sj]
                            header = ["J"]+branches+["Sum"]

                        vv = mtools.dict_sj.values()
                        total = sum([x*factor for x in vv if x != ph.NO_LINE_STRENGTH])
                        rows.append([J+.5]+["{:.5e}".format(x*factor) if x != ph.NO_LINE_STRENGTH else "-" for x in vv]+["{:.9g}".format(total)])

                    l_text.append(tabulate.tabulate(rows, header))
                    l_text.append("")

            text = "\n".join(l_text)
            self.textEdit.setPlainText(text)
            self.status("")
        except Exception as E:
            self.add_log_error(a99.str_exc(E), True)




class WMolecularConstants(a99.WBase):
    """
    Widget for the user to type or obtain many molecular constants
    """

    @property
    def moldb(self):
        return self._moldb

    @property
    def molconsts(self):
        return self._molconsts

    @molconsts.setter
    def molconsts(self, molconsts):
        self._molconsts = molconsts
        self._update_gui()

    @property
    def fcfs(self):
        """Returns a dictionary of Franck-Condon Factors (key is (vl, v2l)), or None"""
        return self._get_fcf_dict()

    @property
    def id_molecule(self):
        return self._get_id_molecule()

    @property
    def flag_valid(self):
        return self._flag_valid

    # @property
    # def row(self):
    #     """Wraps WDBMolecule.row"""
    #     return self.w_mol.row

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        self._molconsts = ft.MolConsts()
        self._flag_valid = True

        # activated when populating table
        self._flag_populating = False
        # # _flag_populating_* collection
        self._flag_populating_molecule = False
        self._flag_populating_system = False
        self._flag_populating_states = False
        self._flag_populating_pfantmol = False
        self._flag_updating_gui = False

        # activated when searching for statel, state2l
        self._flag_searching_states = False
        # activated when searching for pfantmol
        self._flag_searching_pfantmol = False
        # activated when searching for system
        self._flag_searching_system = False

        # # Internal state

        # FileMolDB object, auxiliary object needed for operations
        self._moldb = None

        # Fields of interest from table 'pfantmol'
        # TODO cro disabled but still left to get rid of this field in the same way I got rid of pfantmol.s
        self._fieldnames_pfantmol = ["fe", "do", "am", "bm", "ua", "ub", "te", ]
        # Fields of interest from table 'state'
        self._fieldnames_state = ["omega_e", "omega_ex_e", "omega_ey_e", "B_e", "alpha_e", "D_e",
                                 "beta_e", "A"]
        # Fields of interest from table 'system'
        self._fieldnames_system = ["from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf"]
        self._flag_built_edits = False
        for fn in self._fieldnames_state:
            assert fn not in self._fieldnames_pfantmol
            assert fn not in self._fieldnames_system
        for fn in self._fieldnames_pfantmol:
            assert fn not in self._fieldnames_system
        self._fieldnames = []  # will be filled in later copy.copy(self._fieldnames_pfantmol)
        # self._fieldnames.extend(self._fieldnames_state)
        # self._fieldnames.extend(self._fieldnames_system)

        # dictionary {(field name): (edit object), }
        # (will be populated later below together with edit widgets creation)
        self._edit_map = {}
        self._edit_map_statel = {}
        self._edit_map_state2l = {}
        self._edit_map_pfantmol = {}
        self._edit_map_system = {}

        # id from table 'molecule'. In sync with combobox_molecule items
        self._ids_molecule = []
        # id from table 'pfantmol'. In sync with combobox_pfantmol
        self._ids_pfantmol = []
        # id from table 'state'. In sync with combobox_statel and combobox_state2l
        self._ids_state = []
        # id from table 'system'. In sync with combobox_system
        self._ids_system = []

        # # GUI design

        l = self.layout_main = QVBoxLayout(self)
        a99.set_margin(l, _LAYMN_MAIN)
        l.setSpacing(_LAYSP_MAIN)


        # ## Select molecule combobox
        l0 = self.layout_molecule = QHBoxLayout()
        l.addLayout(l0)
        l0.setSpacing(_LAYSP_CB)
        la = self.label_molecule = QLabel()
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l0.addWidget(la)
        cb = self.combobox_molecule = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_molecule_currentIndexChanged)
        l0.addWidget(cb)

        la.setBuddy(cb)

        # ## Frame with the combobox to select the "system"

        fr = self.frame_system = a99.get_frame()
        l.addWidget(fr)
        l1 = self.layout_frame_system = QVBoxLayout(fr)
        l1.setSpacing(_LAYSP_V)
        a99.set_margin(l1, _LAYMN_V)

        # ### Select system combobox
        l2 = self.layout_system = QHBoxLayout()
        l1.addLayout(l2)
        l2.setSpacing(_LAYSP_CB)
        la = self.label_system = QLabel()
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l2.addWidget(la)
        cb = self.combobox_system = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_system_currentIndexChanged)
        l2.addWidget(cb)

        la.setBuddy(cb)

        la = self.label_fcf = QLabel()
        la.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        l2.addWidget(la)


        # ### State constants edit fields

        lg = self.layout_grid_system = QGridLayout()
        l1.addLayout(lg)
        a99.set_margin(lg, _LAYMN_GRID)
        lg.setSpacing(_LAYSP_GRID)

        # #### Frame for pfantmol combobox end edit fields


        lfp = self.layout_outer_frame_pfantmol = QVBoxLayout()
        l1.addLayout(lfp)
        lfp.setSpacing(_LAYSP_FRAME1)
        lfp.setContentsMargins(_LAYMN_FRAME1, 0, _LAYMN_FRAME1, _LAYMN_FRAME1, )

        fr = self.frame_pfantmol = a99.get_frame()
        lfp.addWidget(fr)
        l5 = self.layout_frame_pfantmol = QVBoxLayout(fr)
        l5.setSpacing(_LAYSP_V)
        a99.set_margin(l5, _LAYMN_V)

        # ##### Label and combobox in H layout
        l55 = self.layout_pfantmol = QHBoxLayout()
        l5.addLayout(l55)
        l55.setSpacing(_LAYSP_CB)

        la = self.label_pfantmol = QLabel("<b>&PFANT molecule</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l55.addWidget(la)

        cb = self.combobox_pfantmol = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_pfantmol_currentIndexChanged)
        l55.addWidget(cb)

        la.setBuddy(cb)

        # ##### PFANT Molecular constants edit fields
        lg = self.layout_grid_pfantmol = QGridLayout()
        a99.set_margin(lg, _LAYMN_GRID)
        lg.setSpacing(_LAYSP_GRID)
        l5.addLayout(lg)


        # #### Statel and State2l

        fr = self.frame_states = a99.get_frame()
        self.layout_main.addWidget(fr)

        l33 = self.layout_frame_states = QVBoxLayout(fr)
        l33.setSpacing(_LAYSP_V)
        a99.set_margin(l33, _LAYMN_V)

        la = self.label_states = QLabel("<b>Constants for individual states</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l33.addWidget(la)

        # This layout will have two frames layed horizontally
        lll = self.layout_states = QHBoxLayout()
        lll.setSpacing(_LAYSP_FRAME1)
        lll.setContentsMargins(_LAYMN_FRAME1, 0, _LAYMN_FRAME1, _LAYMN_FRAME1, )
        l33.addLayout(lll)

        # ##### Frame for Diatomic molecular constants for statel

        fr = self.frame_statel = a99.get_frame()
        lll.addWidget(fr)
        l3 = self.layout_frame_statel = QVBoxLayout(fr)
        l3.setSpacing(_LAYSP_V)
        a99.set_margin(l3, _LAYMN_V)

        # ###### Select statel combobox
        l4 = self.layout_statel = QHBoxLayout()
        l3.addLayout(l4)
        l4.setSpacing(_LAYSP_CB)
        la = self.label_statel = QLabel("<b>Diatomic molecular constants for state'</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l4.addWidget(la)
        cb = self.combobox_statel = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_statel_currentIndexChanged)
        l4.addWidget(cb)

        la.setBuddy(cb)

        # ###### Statel edit fields

        lg = self.layout_grid_statel = QGridLayout()
        a99.set_margin(lg, _LAYMN_GRID)
        lg.setSpacing(_LAYSP_GRID)
        l3.addLayout(lg)


        # ##### Frame for Diatomic molecular constants for state2l

        fr = self.frame_state2l = a99.get_frame()
        lll.addWidget(fr)
        l3 = self.layout_frame_state2l = QVBoxLayout(fr)
        l3.setSpacing(_LAYSP_V)
        a99.set_margin(l3, _LAYMN_V)

        # ###### Select state2l combobox
        l4 = self.layout_state2l = QHBoxLayout()
        l3.addLayout(l4)
        l4.setSpacing(_LAYSP_CB)
        la = self.label_state2l = QLabel("<b>Diatomic molecular constants for state''</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l4.addWidget(la)
        cb = self.combobox_state2l = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_state2l_currentIndexChanged)
        l4.addWidget(cb)

        la.setBuddy(cb)

        # ###### State2l edit fields

        lg = self.layout_grid_state2l = QGridLayout()
        a99.set_margin(lg, _LAYMN_GRID)
        lg.setSpacing(_LAYSP_GRID)
        l3.addLayout(lg)


        # ## Toolbar at bottom
        ltb = self.layout_toolbar = QHBoxLayout()
        self.layout_main.addLayout(ltb)
        a99.set_margin(ltb, _LAYMN_TOOLBAR)
        ltb.setSpacing(_LAYSP_TOOLBAR)

        ltb.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        bb = self.button_zeros = QPushButton("Fill empty fields with zeros")
        bb.clicked.connect(self.None_to_zero)
        ltb.addWidget(bb)

        bb = self.button_zeros = QPushButton("View Hönl-London factors")
        bb.clicked.connect(self.view_hlf)
        ltb.addWidget(bb)

        a99.nerdify(self)

    def __getitem__(self, fieldname):
        return self.molconsts[fieldname]

    def __setitem__(self, fieldname, value):
        """Can assign widget properties by key. TODO Does not work with id_* yet"""
        if fieldname not in self._fieldnames:
            raise KeyError("Invalid fieldname '{}'".format(fieldname))

        widget = self._edit_map[fieldname]
        text = str(value) if value is not None else ""
        widget.setText(text)


    def set_moldb(self, fobj):
        import f311.filetypes as ft
        assert isinstance(fobj, ft.FileMolDB), "I dont want a {}".format(fobj)

        self._moldb = fobj

        if fobj is not None:
            self._populate()
            self._update_gui()
            # self._auto_search()


    def None_to_zero(self):
        """Fills missing values with zeros"""
        for edit in self._edit_map.values():
            if len(edit.text().strip()) == 0:
                edit.setText("0")

        self._update_molconsts()

    def view_hlf(self):
        """Opens text window with HLFs on them"""


        if self.moldb is None:
            a99.show_error("Cannot view HLFs because I need a molecular constants database")
        elif self.molconsts is None:
            a99.show_error("Cannot view HLFs because I am blank")
        else:
            form = _XHLF(self, self.moldb, self.molconsts, self._get_fcf_dict())
            form.show()


    ################################################################################################
    # # Qt override

    def eventFilter(self, obj_focused, event):
        if event.type() == QEvent.FocusIn:
            if obj_focused in self._edit_map.values():
                self.status(obj_focused.toolTip())
        return False

    ################################################################################################
    # # Slots

    def _onTextEdited(self):
        self._update_molconsts()
        self.changed.emit()

    def combobox_molecule_currentIndexChanged(self):
        if self._flag_updating_gui:
            return
        if self._flag_populating_molecule:
            return

        self._populate_sub_comboboxes()
        self._auto_search()
        self._update_molconsts()
        self.changed.emit()

    def combobox_system_currentIndexChanged(self):
        if self._flag_updating_gui:
            return
        if self._flag_populating_system:
            return
        if self._flag_searching_system:
            return

        self._fill_edits_system()
        self._update_label_fcf()

        self._populate_combobox_pfantmol()

        self._auto_search_states()
        self._auto_search_pfantmol()
        self._update_molconsts()
        self.changed.emit()

    def combobox_pfantmol_currentIndexChanged(self):
        if self._flag_updating_gui:
            return
        if self._flag_populating_pfantmol:
            return
        if self._flag_searching_pfantmol:
            return

        self._fill_edits_pfantmol()
        self._update_molconsts()
        self.changed.emit()

    def combobox_statel_currentIndexChanged(self):
        if self._flag_updating_gui:
            return
        if self._flag_populating_states:
            return
        if self._flag_searching_states:
            return

        self._fill_edits_statel()
        self._update_molconsts()
        self.changed.emit()

    def combobox_state2l_currentIndexChanged(self):
        if self._flag_updating_gui:
            return
        if self._flag_populating_states:
            return
        if self._flag_searching_states:
            return

        self._fill_edits_state2l()
        self._update_molconsts()
        self.changed.emit()

    ################################################################################################
    # # Internal function

    def _get_id_molecule(self):
        idx = self.combobox_molecule.currentIndex()
        if idx > 0:
            return self._ids_molecule[idx-1]
        return None

    def _get_id_pfantmol(self):
        idx = self.combobox_pfantmol.currentIndex()
        if idx > 0:
            return self._ids_pfantmol[idx-1]
        return None

    def _get_id_statel(self):
        idx = self.combobox_statel.currentIndex()
        if idx > 0:
            return self._ids_state[idx-1]
        return None

    def _get_id_state2l(self):
        idx = self.combobox_state2l.currentIndex()
        if idx > 0:
            return self._ids_state[idx-1]
        return None

    def _get_id_system(self):
        idx = self.combobox_system.currentIndex()
        if idx > 0:
            return self._ids_system[idx - 1]
        return None

    def _get_fcf_dict(self):
        if self.moldb is None:
            return None
        return self.moldb.get_fcf_dict(self._get_id_system())

    def _populate(self):
        if not self._flag_built_edits:
            self._build_edits()
        self._populate_combobox_molecule()
        self._populate_sub_comboboxes()

    def _populate_sub_comboboxes(self):
        self._populate_combobox_system()
        self._populate_combobox_pfantmol()
        self._populate_combobox_state()

    def _populate_combobox_molecule(self):
        if self._flag_populating_molecule:
            return

        self._flag_populating_molecule = True
        try:
            cb = self.combobox_molecule
            cb.clear()
            self._ids_molecule = []
            data = self.moldb.query_molecule().fetchall()
            cb.addItem("(please select)" if len(data) > 0 else "(no data)")
            for row in data:
                    cb.addItem("{:10} {}".format(row["formula"], row["name"]))
                    self._ids_molecule.append(row["id"])
            self._set_caption_molecule()

        finally:
            self._flag_populating_molecule = False

    def _populate_combobox_pfantmol(self):
        if self._flag_populating_pfantmol:
            return

        self._flag_populating_pfantmol = True
        try:
            cb = self.combobox_pfantmol
            cb.clear()
            self._ids_pfantmol = []

            id_system = self._get_id_system()

            if id_system is not None:
                data = self.moldb.query_pfantmol(id_system=self._get_id_system()).fetchall()
                cb.addItem("(please select)" if len(data) > 0 else "(no data)")
                for row in data:
                    cb.addItem("{}".format(row["description"]))
                    self._ids_pfantmol.append(row["id"])

            self._fill_edits_pfantmol()
            self._set_caption_pfantmol()
        finally:
            self._flag_populating_pfantmol = False

    def _populate_combobox_state(self):
        if self._flag_populating_states:
            return

        self._flag_populating_states = True
        try:
            self._ids_state = []
            data = self.moldb.query_state(id_molecule=self._get_id_molecule()).fetchall()
            cb = self.combobox_statel
            cb.clear()
            cb.addItem("(please select)" if len(data) > 0 else "(no data)")
            for row in data:
                cb.addItem("{}".format(row["State"]))
                self._ids_state.append(row["id"])

            cb = self.combobox_state2l
            cb.clear()
            cb.addItem("(please select)" if len(data) > 0 else "(no data)")
            for row in data:
                cb.addItem("{}".format(row["State"]))

            self._set_caption_state()

        finally:
            self._flag_populating_states = False

    def _populate_combobox_system(self):
        if self._flag_populating_system:
            return

        self._flag_populating_system = True
        try:
            cb = self.combobox_system
            cb.clear()
            self._ids_system = []
            data = self.moldb.query_system(id_molecule=self._get_id_molecule()).fetchall()
            cb.addItem("(please select)" if len(data) > 0 else "(no data)")
            for row in data:
                cb.addItem(ft.molconsts_to_system_str(row, style=ft.SS_ALL_SPECIAL))
                self._ids_system.append(row["id"])

            self._fill_edits_system()
            self._update_label_fcf()
            self._set_caption_system()

        finally:
            self._flag_populating_system = False

    def _build_edits(self):
        self._build_edits_generic(6, self._fieldnames_system, "system", self.layout_grid_system, self._edit_map_system)
        self._build_edits_generic(4, self._fieldnames_pfantmol, "pfantmol", self.layout_grid_pfantmol, self._edit_map_pfantmol)
        self._build_edits_generic(4, self._fieldnames_state, "state", self.layout_grid_statel, self._edit_map_statel, "statel_")
        self._build_edits_generic(4, self._fieldnames_state, "state", self.layout_grid_state2l, self._edit_map_state2l, "state2l_")
        self._flag_built_edits = True

    def _build_edits_generic(self, nc, fieldnames, tablename, layout, edit_map, fieldname_all_prefix=""):

        def new_spacer():
            w = QWidget(self)
            self.keep_ref(w)
            #w.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum))
            w.setFixedWidth(_SPACE_BETWEEN_FIELDS)
            return w



        n = len(fieldnames)
        ti = self.moldb.get_table_info(tablename)
        for k in range(n):
            i = k // nc
            j = k % nc

            fieldname = fieldnames[k]
            fieldname_all = fieldname_all_prefix+fieldname

            info = ti[fieldname]
            caption = info["caption"] or fieldname
            a = QLabel(caption)
            e = QLineEdit("")
            e.textEdited.connect(self._onTextEdited)
            e.installEventFilter(self)
            tooltip = info["tooltip"]
            if tooltip:
                a.setToolTip(tooltip)
                e.setToolTip(tooltip)
            self._fieldnames.append(fieldname_all)
            self._edit_map[fieldname_all] = e
            edit_map[fieldname] = e
            layout.addWidget(a, i, j * 3)
            layout.addWidget(e, i, j * 3 + 1)
            if j < nc-1:
                layout.addWidget(new_spacer(), i, j*3+2)

    def _fill_edits_pfantmol(self):
        id_ = self._get_id_pfantmol()
        if id_ is not None:
            row = self.moldb.query_pfantmol(**{"pfantmol.id": id_}).fetchone()
            for fieldname, e in self._edit_map_pfantmol.items():
                v = row[fieldname]
                e.setText(str(v) if v is not None else "")

    def _fill_edits_statel(self):
        id_ = self._get_id_statel()
        if id_ is not None:
            row = self.moldb.query_state(**{"state.id": id_}).fetchone()
            for fieldname, e in self._edit_map_statel.items():
                v = row[fieldname]
                e.setText(str(v) if v is not None else "")

    def _fill_edits_state2l(self):
        id_ = self._get_id_state2l()
        if id_ is not None:
            row = self.moldb.query_state(**{"state.id": id_}).fetchone()
            for fieldname, e in self._edit_map_state2l.items():
                v = row[fieldname]
                e.setText(str(v) if v is not None else "")


    def _fill_edits_system(self):
        id_ = self._get_id_system()
        if id_ is not None:
            row = self.moldb.query_system(**{"system.id": id_}).fetchone()
            for fieldname, e in self._edit_map_system.items():
                v = row[fieldname]
                e.setText(str(v) if v is not None else "")

    def _update_label_fcf(self):
        n, fcfs = 0, self._get_fcf_dict()
        if fcfs is not None:
            n = len(fcfs)
        # Left space to take a distance from combobox left to it
        s = '<font color="{}">{}Franck-Condon Factors (FCFs) for {} vibrational transition{}</font>'.\
            format("blue" if n != 0 else "red",
                   "",
                   n,
                   "" if n == 1 else "s")
        self.label_fcf.setText(s)

    def _auto_search(self):
        self._auto_search_system()
        self._populate_combobox_pfantmol()
        self._auto_search_pfantmol()
        self._auto_search_states()

    def _auto_search_system(self):
        if self._flag_populating_system or self._flag_searching_system:
            return

        self._flag_searching_system = True
        try:
            if len(self._ids_system) > 0:
                self.combobox_system.setCurrentIndex(1)
                self._fill_edits_system()
                self._update_label_fcf()
        finally:
            self._flag_searching_system = False

    def _auto_search_pfantmol(self):
        if self._flag_populating_pfantmol or self._flag_searching_pfantmol:
            return

        self._flag_searching_pfantmol = True
        try:
            if len(self._ids_pfantmol) > 0:
                self.combobox_pfantmol.setCurrentIndex(1)
                self._fill_edits_pfantmol()
        finally:
            self._flag_searching_pfantmol = False

    def _auto_search_states(self):

        if self._flag_populating_states or self._flag_searching_states:
            return

        self._flag_searching_states = True
        try:
            self.__auto_search_state("from_label")
            self.__auto_search_state("to_label")
        finally:
            self._flag_searching_states = False

    def __auto_search_state(self, fieldname="from_label"):
        cb = self.combobox_statel if fieldname == "from_label" else self.combobox_state2l
        id_molecule = self._get_id_molecule()
        if id_molecule is not None:
            id_system = self._get_id_system()
            if id_system is not None:
                row_system = self.moldb.query_system(id=id_system).fetchone()

                state = row_system[fieldname]
                row_state = self.moldb.get_conn().execute("select * from state where id_molecule = ? "
                 "and substr(State, 1, {}) = ?".format(len(state)), (id_molecule, state,)).fetchone()

                if row_state is not None:
                    cb.setCurrentIndex(self._ids_state.index(row_state["id"]) + 1)
                    if fieldname == "from_label":
                        self._fill_edits_statel()
                    else:
                        self._fill_edits_state2l()

    def _set_caption_molecule(self):
        self.label_molecule.setText("<b>&Molecule ({})</b>".format(len(self._ids_molecule)))


    def _set_caption_system(self):
        self.label_system.setText("<b>&Electronic system ({})</b>".format(len(self._ids_system)))


    def _set_caption_state(self):
        self.label_statel.setText("<b>State ' ({})</b>".format(len(self._ids_state)))
        self.label_state2l.setText("<b>State '' ({})</b>".format(len(self._ids_state)))

    def _set_caption_pfantmol(self):
        self.label_pfantmol.setText("<b>&PFANT molecule ({})</b>".format(len(self._ids_pfantmol)))


    def _update_gui(self):
        if self._flag_updating_gui:
            return

        def populate_two_comboboxes():
            self._populate_combobox_system()
            self._populate_combobox_state()


        self._flag_updating_gui = True

        try:
            molconsts = self._molconsts

            # map to update the comboboxes
            _CB_MAP = [
                ("id_molecule", self.combobox_molecule, lambda: self._ids_molecule,
                 populate_two_comboboxes),
                ("id_system", self.combobox_system, lambda: self._ids_system,
                 self._populate_combobox_pfantmol),
                ("id_pfantmol", self.combobox_pfantmol, lambda: self._ids_pfantmol, None),
                ("id_statel", self.combobox_statel, lambda: self._ids_state, None),
                ("id_state2l", self.combobox_state2l, lambda: self._ids_state, None),
            ]

            # # Stage 1/2: comboboxes
            for fieldname, cb, f_ids, method_after in _CB_MAP:
                value = molconsts[fieldname]
                if value is not None:
                    try:
                        idx = f_ids().index(value)
                        cb.setCurrentIndex(idx+1)

                        if method_after is not None:
                            method_after()

                    except ValueError:
                        pass  # nevermind, just won't position combobox properly


            # # Stage 2/2: edits
            for fieldname in self._fieldnames:
                self[fieldname] = molconsts[fieldname]

        finally:
            self._update_label_fcf()
            self._flag_updating_gui = False

    def _update_molconsts(self):
        """Updates molconsts from GUI"""

        emsg, flag_error = "", False
        fieldname = None
        try:
            # edits
            for fieldname in self._fieldnames:
                text = self._edit_map[fieldname].text()
                if "_label" in fieldname:
                    # Fields with "_label" in their names are treated as strings,
                    # otherwise they are considered numeric
                    value = text
                else:
                    if len(text.strip()) > 0:
                        value = float(text)
                    else:
                        value = None

                self.molconsts[fieldname] = value

            # comboboxes
            _CB_MAP = [
                ("id_molecule", self.combobox_molecule, lambda: self._ids_molecule),
                ("id_system", self.combobox_system, lambda: self._ids_system),
                ("id_pfantmol", self.combobox_pfantmol, lambda: self._ids_pfantmol),
                ("id_statel", self.combobox_statel, lambda: self._ids_state),
                ("id_state2l", self.combobox_state2l, lambda: self._ids_state),
            ]

            for fieldname, cb, f_ids in _CB_MAP:
                idx = cb.currentIndex()
                if idx > 0:
                    self._molconsts[fieldname] = f_ids()[idx-1]


            fieldname = None
            # Values that must be in sync with some id's
            id_ = self._molconsts["id_molecule"]
            if id_ is not None:
                row = self._moldb.query_molecule(id=id_).fetchone()
                self._molconsts["formula"] = row["formula"]
                self._molconsts["name"] = row["name"]

            id_ = self._molconsts["id_pfantmol"]
            if id_ is not None:
                row = self._moldb.query_pfantmol(id=id_).fetchone()
                self._molconsts["description"] = row["description"]


        except Exception as E:
            flag_error = True
            if fieldname is not None:
                emsg = "Field '{}': {}".format(fieldname, str(E))
            else:
                emsg = str(E)
            self.add_log_error(emsg, E=E)


        self._flag_valid = not flag_error
        if not flag_error:
            self.status("")

