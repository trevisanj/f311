from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
from .a_WDBState import WDBState
import copy
import f311.filetypes as ft

__all__ = ["WMolecularConstants"]


class WMolecularConstants(a99.WBase):
    """
    Widget for the user to type or obtain many molecular constants
    """

    @property
    def f(self):
        """Object representing the file being edited (possibly a DataFile object)"""
        return self.moldb

    @f.setter
    def f(self, f):
        self.load(f)

    @property
    def constants(self):
        """Returns a dictionary that combines several records (see details):

        - one record from table 'molecule'
        - one record from table 'system'
        - one record from table 'pfantmol'
        - two records from table 'state', for state' and state''
            * keys for state' values start with "statel_"
            * keys for state'' values start with "state2l_"
        """
        ret = ft.MolConsts()
        for fieldname in self._fieldnames:
            ret[fieldname] = self[fieldname]
        ret["name"] = self.name
        ret["formula"] = self.formula
        return ret

    @property
    def name(self):
        """Returns molecule 'name' (field from 'molecule' table)"""
        ret, id_ = None, self._get_id_molecule()
        if id_ is not None:
            ret = self.moldb.get_conn().execute("select name from molecule where id = ?", (id_,)).fetchone()["name"]
        return ret

    @property
    def formula(self):
        """Returns molecule 'formula' (field from 'molecule' table)"""
        ret, id_ = None, self._get_id_molecule()
        if id_ is not None:
            ret = self.moldb.get_conn().execute("select formula from molecule where id = ?", (id_,)).fetchone()["formula"]
        return ret

    @property
    def fcfs(self):
        """Returns a dictionary of Franck-Condon Factors (key is (vl, v2l)), or None"""
        return self._get_fcf_dict()

    @property
    def id_molecule(self):
        return self._get_id_molecule()

    # @property
    # def row(self):
    #     """Wraps WDBMolecule.row"""
    #     return self.w_mol.row

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        # activated when populating table
        self._flag_populating = False
        # # _flag_populating_* collection
        self._flag_populating_molecule = False
        self._flag_populating_system = False
        self._flag_populating_states = False
        self._flag_populating_pfantmol = False

        # activated when searching for statel, state2l
        self._flag_searching_states = False
        # activated when searching for pfantmol
        self._flag_searching_pfantmol = False

        # # Internal state

        # FileMolDB object, I guess
        self.moldb = None

        # Fields of interest from table 'pfantmol'
        self._fieldnames_pfantmol = ["fe", "do", "am", "bm", "ua", "ub", "te", "cro", ]
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
        a99.set_margin(l, 2)
        l.setSpacing(6)

        # ## Toolbar at top
        bb = self.button_zeros = QPushButton("Fill empty fields with zeros")
        bb.clicked.connect(self.None_to_zero)
        l.addWidget(bb)

        # ## Select molecule combobox
        l0 = self.layout_molecule = QHBoxLayout()
        l.addLayout(l0)
        l0.setSpacing(3)
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

        # ### Select system combobox
        l2 = self.layout_system = QHBoxLayout()
        l1.addLayout(l2)
        l2.setSpacing(3)
        la = self.label_system = QLabel()
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l2.addWidget(la)
        cb = self.combobox_system = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_system_currentIndexChanged)
        l2.addWidget(cb)

        la.setBuddy(cb)

        la = self.label_fcf = QLabel()
        la.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        l1.addWidget(la)


        # ### State constants edit fields

        lg = self.layout_grid_system = QGridLayout()
        l1.addLayout(lg)

        # #### Frame for pfantmol combobox end edit fields



        fr = self.frame_pfantmol = a99.get_frame()
        l1.addWidget(fr)
        l5 = self.layout_frame_pfantmol = QVBoxLayout(fr)
        l5.setSpacing(3)

        # ##### Label and combobox in H layout
        l55 = self.layout_pfantmol = QHBoxLayout()
        l5.addLayout(l55)
        l55.setSpacing(3)

        la = self.label_pfantmol = QLabel("<b>&PFANT molecule</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l55.addWidget(la)

        cb = self.combobox_pfantmol = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_pfantmol_currentIndexChanged)
        l55.addWidget(cb)

        la.setBuddy(cb)

        # ##### PFANT Molecular constants edit fields
        lg = self.layout_grid_pfantmol = QGridLayout()
        l5.addLayout(lg)



        # #### Frame for Diatomic molecular constants for statel

        fr = self.frame_statel = a99.get_frame()
        l.addWidget(fr)
        l3 = self.layout_frame_statel = QVBoxLayout(fr)

        # ##### Select statel combobox
        l4 = self.layout_statel = QHBoxLayout()
        l3.addLayout(l4)
        l4.setSpacing(3)
        la = self.label_statel = QLabel("<b>Diatomic molecular constants for state'</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l4.addWidget(la)
        cb = self.combobox_statel = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_statel_currentIndexChanged)
        l4.addWidget(cb)

        la.setBuddy(cb)

        # ##### Statel edit fields

        lg = self.layout_grid_statel = QGridLayout()
        l3.addLayout(lg)



        # #### Frame for Diatomic molecular constants for state2l

        fr = self.frame_state2l = a99.get_frame()
        l.addWidget(fr)
        l3 = self.layout_frame_state2l = QVBoxLayout(fr)

        # ##### Select state2l combobox
        l4 = self.layout_state2l = QHBoxLayout()
        l3.addLayout(l4)
        l4.setSpacing(3)
        la = self.label_state2l = QLabel("<b>Diatomic molecular constants for state''</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l4.addWidget(la)
        cb = self.combobox_state2l = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_state2l_currentIndexChanged)
        l4.addWidget(cb)

        la.setBuddy(cb)

        # ##### State2l edit fields

        lg = self.layout_grid_state2l = QGridLayout()
        l3.addLayout(lg)




        a99.nerdify(self)

    def __getitem__(self, fieldname):
        """Allows dict-like access of molecular constants of interest. Returns float value or None"""
        if fieldname in self._fieldnames:
            text = self._edit_map[fieldname].text()
            if "_label" in fieldname:
                # Fields with "_label" in their names are treated as strings,
                # otherwise they are considered numeric
                return text.upper()
            else:
                try:
                    return float(text)
                except ValueError:
                    return None


    def load(self, moldb):
        """Loads a FileMolDB object"""
        import f311.filetypes as ft
        assert isinstance(moldb, ft.FileMolDB)

        self.moldb = moldb
        if moldb is not None:
            self._populate()
            self._auto_search()


    def None_to_zero(self):
        """Fills missing values with zeros"""
        for edit in self._edit_map.values():
            if len(edit.text().strip()) == 0:
                edit.setText("0")

    ################################################################################################
    # # Qt override

    def eventFilter(self, obj_focused, event):
        if event.type() == QEvent.FocusIn:
            if obj_focused in self._edit_map.values():
                self.status(obj_focused.toolTip())
        return False

    ################################################################################################
    # # Slots

    def combobox_molecule_currentIndexChanged(self):
        if self._flag_populating_molecule:
            return

        self._populate_sub_comboboxes()
        self._auto_search()

    def combobox_pfantmol_currentIndexChanged(self):
        if self._flag_populating_pfantmol:
            return

        self._fill_edits_pfantmol()

    def combobox_statel_currentIndexChanged(self):
        if self._flag_populating_states:
            return

        self._fill_edits_statel()

    def combobox_state2l_currentIndexChanged(self):
        if self._flag_populating_states:
            return

        self._fill_edits_state2l()

    def combobox_system_currentIndexChanged(self):
        if self._flag_populating_system:
            return

        self._fill_edits_system()
        self._update_label_fcf()

        self._populate_combobox_pfantmol()

        self._auto_search_states()
        self._auto_search_pfantmol()

    ################################################################################################
    # # Internal function

    def _get_id_molecule(self):
        if len(self._ids_molecule) > 0:
            return self._ids_molecule[self.combobox_molecule.currentIndex()]
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
        if len(self._ids_system) > 0:
            return self._ids_system[self.combobox_system.currentIndex()]
        return None

    def _get_fcf_dict(self):
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
            cursor = self.moldb.query_molecule()
            for row in cursor:
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
                cb.addItem("(select to fill information below)" if len(data) > 0 else "(no data)")
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
            cb.addItem("(select to fill information below)" if len(data) > 0 else "(no data)")
            for row in data:
                cb.addItem("{}".format(row["State"]))
                self._ids_state.append(row["id"])

            cb = self.combobox_state2l
            cb.clear()
            cb.addItem("(select to fill information below)" if len(data) > 0 else "(no data)")
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
            if len(data) == 0:
                cb.addItem("(no data)")
            for row in data:
                cb.addItem(ft.molconsts_to_system_str(row, style=ft.SS_ALL_SPECIAL))
                self._ids_system.append(row["id"])

            self._fill_edits_system()
            self._update_label_fcf()
            self._set_caption_system()

        finally:
            self._flag_populating_system = False

    def _build_edits(self):
        # pfantmol fields
        nr, nc, n = 3, 3, len(self._fieldnames_pfantmol)
        ti = self.moldb.get_table_info("pfantmol")
        lg = self.layout_grid_pfantmol
        for j in range(nc):
            # ### One grid layout for each column of fields
            ii = range(j, n, nc)
            for i in range(len(ii)):
                fieldname = self._fieldnames_pfantmol[ii[i]]
                info = ti[fieldname]
                caption = info["caption"] or fieldname
                a = QLabel(caption)
                e = QLineEdit("")
                e.installEventFilter(self)
                tooltip = info["tooltip"]
                if tooltip:
                    a.setToolTip(tooltip)
                    e.setToolTip(tooltip)
                self._fieldnames.append(fieldname)
                self._edit_map[fieldname] = e
                self._edit_map_pfantmol[fieldname] = e
                lg.addWidget(a, i, j * 2)
                lg.addWidget(e, i, j * 2 + 1)

        # system fields
        nr, nc, n = 2, 3, len(self._fieldnames_system)
        ti = self.moldb.get_table_info("system")
        lg = self.layout_grid_system
        for j in range(nc):
            # ### One grid layout for each column of fields
            ii = range(j, n, nc)
            for i in range(len(ii)):
                fieldname = self._fieldnames_system[ii[i]]
                info = ti[fieldname]
                caption = info["caption"] or fieldname
                a = QLabel(caption)
                e = QLineEdit("")
                e.installEventFilter(self)
                tooltip = info["tooltip"]
                if tooltip:
                    a.setToolTip(tooltip)
                    e.setToolTip(tooltip)
                self._fieldnames.append(fieldname)
                self._edit_map[fieldname] = e
                self._edit_map_system[fieldname] = e
                lg.addWidget(a, i, j * 2)
                lg.addWidget(e, i, j * 2 + 1)

        # statel fields
        nr, nc, n = 3, 3, len(self._fieldnames_state)
        ti = self.moldb.get_table_info("state")
        lg = self.layout_grid_statel
        for j in range(nc):
            # ### One grid layout for each column of fields
            ii = range(j, n, nc)
            for i in range(len(ii)):
                fieldname = self._fieldnames_state[ii[i]]
                info = ti[fieldname]
                caption = info["caption"] or fieldname
                a = QLabel(caption)
                e = QLineEdit("")
                e.installEventFilter(self)
                tooltip = info["tooltip"]
                if tooltip:
                    a.setToolTip(tooltip)
                    e.setToolTip(tooltip)
                fieldname_all = "statel_" + fieldname
                self._fieldnames.append(fieldname_all)
                self._edit_map[fieldname_all] = e
                self._edit_map_statel[fieldname] = e
                lg.addWidget(a, i, j * 2)
                lg.addWidget(e, i, j * 2 + 1)

        # statel fields
        nr, nc, n = 3, 3, len(self._fieldnames_state)
        ti = self.moldb.get_table_info("state")
        lg = self.layout_grid_state2l
        for j in range(nc):
            # ### One grid layout for each column of fields
            ii = range(j, n, nc)
            for i in range(len(ii)):
                fieldname = self._fieldnames_state[ii[i]]
                info = ti[fieldname]
                caption = info["caption"] or fieldname
                a = QLabel(caption)
                e = QLineEdit("")
                e.installEventFilter(self)
                tooltip = info["tooltip"]
                if tooltip:
                    a.setToolTip(tooltip)
                    e.setToolTip(tooltip)
                fieldname_all = "state2l_" + fieldname
                self._fieldnames.append(fieldname_all)
                self._edit_map[fieldname_all] = e
                self._edit_map_state2l[fieldname] = e
                lg.addWidget(a, i, j * 2)
                lg.addWidget(e, i, j * 2 + 1)

        self._flag_built_edits = True


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
        s = '<font color="{}">Franck-Condon Factors (FCFs) for {} vibrational transition{}</font>'.\
            format("blue" if n != 0 else "red", n, "" if n == 1 else "s")
        self.label_fcf.setText(s)

    def _auto_search(self):
        self._auto_search_pfantmol()
        self._auto_search_states()

    def _auto_search_pfantmol(self):
        if self._flag_populating_pfantmol or self._flag_searching_pfantmol:
            return

        self._flag_searching_pfantmol = True
        try:
            if len(self._ids_pfantmol) > 0:
                self.combobox_pfantmol.setCurrentIndex(1)
        finally:
            self._flag_searching_pfantmol = False

    def _auto_search_states(self):
        if self._flag_populating_states or self._flag_searching_states:
            return

        self._flag_searching_states = True
        try:
            self.__auto_search_state("from_label")
            self.__auto_search_state("to_label")
            self._fill_edits_statel()
            self._fill_edits_state2l()
        finally:
            self._flag_searching_states = False

    def __auto_search_state(self, fieldname="from_label"):
        cb = self.combobox_statel if fieldname == "from_label" else self.combobox_state2l
        id_molecule = self._get_id_molecule()
        if id_molecule is not None:
            id_system = self._get_id_system()
            if id_system is not None:
                row_system = self.moldb.query_system(id=id_system).fetchone()

                row_state = self.moldb.get_conn().execute("select * from state where id_molecule = ? "
                 "and State like ?", (id_molecule, "{}%".format(row_system[fieldname]),)).fetchone()

                if row_state is not None:
                    try:
                        cb.setCurrentIndex(self._ids_state.index(row_state["id"]) + 1)
                    except ValueError:
                        raise


    def _set_caption_molecule(self):
        self.label_molecule.setText("<b>&Molecule ({})</b>".format(len(self._ids_molecule)))


    def _set_caption_system(self):
        self.label_system.setText("<b>&Electronic system ({})</b>".format(len(self._ids_system)))


    def _set_caption_state(self):
        self.label_statel.setText("<b>State ' ({})</b>".format(len(self._ids_state)))
        self.label_state2l.setText("<b>State '' ({})</b>".format(len(self._ids_state)))

    def _set_caption_pfantmol(self):
        self.label_pfantmol.setText("<b>&PFANT molecule ({})</b>".format(len(self._ids_pfantmol)))