from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
from .a_WDBState import WDBState
import copy

__all__ = ["WMolecularConstants"]


class WMolecularConstants(a99.WBase):
    """
    Widget for the user to type or obtain many molecular constants
    """

    @property
    def f(self):
        """Object representing the file being edited (possibly a DataFile object)"""
        return self._f

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
        ret = {}
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
            ret = self._f.get_conn().execute("select name from molecule where id = ?", (id_,)).fetchone()["name"]
        return ret

    @property
    def formula(self):
        """Returns molecule 'formula' (field from 'molecule' table)"""
        ret, id_ = None, self._get_id_molecule()
        if id_ is not None:
            ret = self._f.get_conn().execute("select formula from molecule where id = ?", (id_,)).fetchone()["formula"]
        return ret

    @property
    def fcfs(self):
        """Returns a dictionary of Franck-Condon Factors (key is (vl, v2l)), or None"""
        return self._get_fcfs()

    @property
    def id_molecule(self):
        return self._get_id_molecule()

    # @property
    # def row(self):
    #     """Wraps WDBMolecule.row"""
    #     return self.w_mol.row

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        self.flag_populating = False  # activated when populating table

        # # Internal state

        # Fields of interest from table 'pfantmol'
        self._fieldnames_pfantmol = ["fe", "do", "am", "bm", "ua", "ub", "te", "cro", "s", ]
        # Fields of interest from table 'state'
        self._fieldnames_state = ["omega_e", "omega_ex_e", "omega_ey_e", "B_e", "alpha_e", "D_e",
                                 "beta_e", "A"]
        # Fields of interest from table 'system'
        self._fieldnames_system = ["from_label", "from_spdf", "to_label", "to_spdf"]
        self._flag_built_edits = False
        for fn in self._fieldnames_state:
            assert fn not in self._fieldnames_pfantmol
            assert fn not in self._fieldnames_system
        for fn in self._fieldnames_pfantmol:
            assert fn not in self._fieldnames_system
        self._fieldnames = copy.copy(self._fieldnames_pfantmol)
        self._fieldnames.extend(self._fieldnames_state)
        self._fieldnames.extend(self._fieldnames_system)

        # dictionary {(field name): (edit object), }
        # (will be populated later below together with edit widgets creation)
        self._edit_map = {}
        self._edit_map_statel = {}
        self._edit_map_state2l = {}
        self._edit_map_pfantmol = {}
        self._edit_map_system = {}

        # id from table 'molecule'. In sync with combobox_select_molecule items
        self._ids_molecule = []
        # id from table 'pfantmol'. In sync with combobox_select_pfantmol
        self._ids_pfantmol = []
        # id from table 'state'. In sync with combobox_select_statel and combobox_state2l
        self._ids_state = []
        # id from table 'system'. In sync with combobox_select_system
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
        l0 = self.layout_select_molecule = QHBoxLayout()
        l.addLayout(l0)
        l0.setSpacing(3)
        la = self.label_select_molecule = QLabel("<b>Molecule</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l0.addWidget(la)
        cb = self.combobox_select_molecule = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_select_molecule_currentIndexChanged)
        l0.addWidget(cb)

        # ## Frame with the PFANT molecule-wide fields

        fr = self.frame_pfantmol = a99.get_frame()
        l.addWidget(fr)
        l1 = self.layout_frame_pfantmol = QVBoxLayout(fr)

        # ### Select pfantmol combobox
        l2 = self.layout_select_pfantmol = QHBoxLayout()
        l1.addLayout(l2)
        l2.setSpacing(3)
        la = self.label_select_pfantmol = QLabel("<b>PFANT molecule</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l2.addWidget(la)
        cb = self.combobox_select_pfantmol = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_select_pfantmol_currentIndexChanged)
        l2.addWidget(cb)

        # ### PFANT Molecular constants edit fields

        lg = self.layout_grid_pfantmol = QGridLayout()
        l1.addLayout(lg)

        # ## Frame with the combobox to select the "system"

        fr = self.frame_system = a99.get_frame()
        l.addWidget(fr)
        l1 = self.layout_frame_system = QVBoxLayout(fr)

        # ### Select system combobox
        l2 = self.layout_select_system = QHBoxLayout()
        l1.addLayout(l2)
        l2.setSpacing(3)
        la = self.label_select_system = QLabel("<b>Electronic system</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l2.addWidget(la)
        cb = self.combobox_select_system = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_select_system_currentIndexChanged)
        l2.addWidget(cb)

        la = self.label_fcf = QLabel()
        la.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        l1.addWidget(la)

        # ### System constants edit fields

        lg = self.layout_grid_system = QGridLayout()
        l1.addLayout(lg)

        # #### Frame for Diatomic molecular constants for statel

        fr = self.frame_statel = a99.get_frame()
        l1.addWidget(fr)
        l3 = self.layout_frame_statel = QVBoxLayout(fr)

        # ##### Select statel combobox
        l4 = self.layout_select_statel = QHBoxLayout()
        l3.addLayout(l4)
        l4.setSpacing(3)
        la = self.label_select_statel = QLabel("<b>Diatomic molecular constants for state'</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l4.addWidget(la)
        cb = self.combobox_select_statel = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_select_statel_currentIndexChanged)
        l4.addWidget(cb)

        # ##### State' edit fields

        lg = self.layout_grid_statel = QGridLayout()
        l3.addLayout(lg)





        # #### Frame for Diatomic molecular constants for state2l

        fr = self.frame_state2l = a99.get_frame()
        l1.addWidget(fr)
        l3 = self.layout_frame_state2l = QVBoxLayout(fr)

        # ##### Select state2l combobox
        l4 = self.layout_select_state2l = QHBoxLayout()
        l3.addLayout(l4)
        l4.setSpacing(3)
        la = self.label_select_state2l = QLabel("<b>Diatomic molecular constants for state''</b>")
        la.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        l4.addWidget(la)
        cb = self.combobox_select_state2l = QComboBox()
        cb.currentIndexChanged.connect(self.combobox_select_state2l_currentIndexChanged)
        l4.addWidget(cb)

        # ##### State' edit fields

        lg = self.layout_grid_state2l = QGridLayout()
        l3.addLayout(lg)









        a99.nerdify(self)

    def __getitem__(self, fieldname):
        """Allows dict-like access of molecular constants of interest. Returns float value or None"""
        if fieldname in self._fieldnames:
            text = self._edit_map[fieldname].text()
            if fieldname in ("from_label", "to_label"):
                # Only two fields to be strings
                return text.upper()
            else:
                try:
                    return float(text)
                except ValueError:
                    return None


    def load(self, f):
        """Loads a FileMolDB object"""
        import f311.filetypes as ft
        assert isinstance(f, ft.FileMolDB)
        self._f = f
        if f is not None:
            self._populate()


    def None_to_zero(self):
        """Fills missing values with zeros"""
        for edit in self._edit_map.values():
            if len(edit.text().strip()) == 0:
                edit.setText("0")

    ################################################################################################
    # # Slots

    def combobox_select_molecule_currentIndexChanged(self):
        self._populate_sub_comboboxes()

    def combobox_select_pfantmol_currentIndexChanged(self):
        self._fill_edits_pfantmol()

    def combobox_select_statel_currentIndexChanged(self):
        self._fill_edits_statel()

    def combobox_select_state2l_currentIndexChanged(self):
        self._fill_edits_state2l()

    def combobox_select_system_currentIndexChanged(self):
        self._fill_edits_system()
        self._update_label_fcf()


    ################################################################################################
    # # Internal function

    def _get_id_molecule(self):
        if len(self._ids_molecule) > 0:
            return self._ids_molecule[self.combobox_select_molecule.currentIndex()]
        return None

    def _get_id_pfantmol(self):
        idx = self.combobox_select_pfantmol.currentIndex()
        if idx > 0:
            return self._ids_pfantmol[idx-1]
        return None

    def _get_id_statel(self):
        idx = self.combobox_select_statel.currentIndex()
        if idx > 0:
            return self._ids_state[idx-1]
        return None

    def _get_id_state2l(self):
        idx = self.combobox_select_state2l.currentIndex()
        if idx > 0:
            return self._ids_state[idx-1]
        return None

    def _get_id_system(self):
        if len(self._ids_system) > 0:
            return self._ids_system[self.combobox_select_system.currentIndex()]
        return None

    def _get_fcfs(self):
        ret, id_ = None, self._get_id_system()
        if id_ is not None:
            _ret = self._f.query_fcf(id_system=id_).fetchall()
            ret = {}
            for r in _ret:
                ret[(r["vl"], r["v2l"])] = r["value"]
        return ret

    def _populate(self):
        if not self._flag_built_edits:
            self._build_edits()
        self._populate_combobox_select_molecule()
        self._populate_sub_comboboxes()

    def _populate_sub_comboboxes(self):
        self._populate_combobox_select_pfantmol()
        self._populate_combobox_select_state()
        self._populate_combobox_select_system()

    def _populate_combobox_select_molecule(self):
        cb = self.combobox_select_molecule
        cb.clear()
        self._ids_molecule = []
        cursor = self._f.query_molecule()
        for row in cursor:
            cb.addItem("{:10} {}".format(row["formula"], row["name"]))
            self._ids_molecule.append(row["id"])

    def _populate_combobox_select_pfantmol(self):
        cb = self.combobox_select_pfantmol
        cb.clear()
        self._ids_pfantmol = []
        data = self._f.query_pfantmol(id_molecule=self._get_id_molecule()).fetchall()
        cb.addItem("(select to fill information below)" if len(data) > 0 else "(no data)")
        for row in data:
            cb.addItem("{}".format(row["description"]))
            self._ids_pfantmol.append(row["id"])
        self._fill_edits_pfantmol()

    def _populate_combobox_select_state(self):
        self._ids_state = []
        data = self._f.query_state(id_molecule=self._get_id_molecule()).fetchall()
        cb = self.combobox_select_statel
        cb.clear()
        cb.addItem("(select to fill information below)" if len(data) > 0 else "(no data)")
        for row in data:
            cb.addItem("{}".format(row["State"]))
            self._ids_state.append(row["id"])

        cb = self.combobox_select_state2l
        cb.clear()
        cb.addItem("(select to fill information below)" if len(data) > 0 else "(no data)")
        for row in data:
            cb.addItem("{}".format(row["State"]))

        self._fill_edits_statel()
        self._fill_edits_state2l()

    def _populate_combobox_select_system(self):
        cb = self.combobox_select_system
        cb.clear()
        self._ids_system = []
        data = self._f.query_system(id_molecule=self._get_id_molecule()).fetchall()
        if len(data) == 0:
            cb.addItem("(no data)")
        for row in data:
            cb.addItem(self._f.get_system_short(row))
            self._ids_system.append(row["id"])
        self._fill_edits_system()
        self._update_label_fcf()


    def __build_edits_generic(self, lg, fn, nc, ti, em):
        """Populates a grid layout with edit fields

        Args:
            lg: QGridLayout
            fn: field names
            nc: number of columns
            ti: dict-like object with information about fields
            em: edit map
        """
        n = len(fn)
        for j in range(nc):
            # ### One grid layout for each column of fields
            ii = range(j, n, nc)
            for i in range(len(ii)):
                fieldname = fn[ii[i]]
                info = ti[fieldname]
                caption = info["caption"] or fieldname
                a = QLabel(caption)
                e = QLineEdit("")
                tooltip = info["tooltip"]
                if tooltip:
                    a.setToolTip(tooltip)
                    e.setToolTip(tooltip)
                self._edit_map[fieldname] = e
                em[fieldname] = e
                lg.addWidget(a, i, j * 2)
                lg.addWidget(e, i, j * 2 + 1)

    def _build_edits(self):
        # pfantmol fields
        nr, nc, n = 3, 3, len(self._fieldnames_pfantmol)
        ti = self._f.get_table_info("pfantmol")
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
                tooltip = info["tooltip"]
                if tooltip:
                    a.setToolTip(tooltip)
                    e.setToolTip(tooltip)
                self._edit_map[fieldname] = e
                self._edit_map_pfantmol[fieldname] = e
                lg.addWidget(a, i, j * 2)
                lg.addWidget(e, i, j * 2 + 1)

        # system fields
        nr, nc, n = 2, 2, len(self._fieldnames_system)
        ti = self._f.get_table_info("system")
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
                tooltip = info["tooltip"]
                if tooltip:
                    a.setToolTip(tooltip)
                    e.setToolTip(tooltip)
                self._edit_map[fieldname] = e
                self._edit_map_system[fieldname] = e
                lg.addWidget(a, i, j * 2)
                lg.addWidget(e, i, j * 2 + 1)

        # statel fields
        nr, nc, n = 3, 3, len(self._fieldnames_state)
        ti = self._f.get_table_info("state")
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
                tooltip = info["tooltip"]
                if tooltip:
                    a.setToolTip(tooltip)
                    e.setToolTip(tooltip)
                self._edit_map["statel_"+fieldname] = e
                self._edit_map_statel[fieldname] = e
                lg.addWidget(a, i, j * 2)
                lg.addWidget(e, i, j * 2 + 1)

        # statel fields
        nr, nc, n = 3, 3, len(self._fieldnames_state)
        ti = self._f.get_table_info("state")
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
                tooltip = info["tooltip"]
                if tooltip:
                    a.setToolTip(tooltip)
                    e.setToolTip(tooltip)
                self._edit_map["state2l_"+fieldname] = e
                self._edit_map_state2l[fieldname] = e
                lg.addWidget(a, i, j * 2)
                lg.addWidget(e, i, j * 2 + 1)


        self._flag_built_edits = True

    def _fill_edits_pfantmol(self):
        id_ = self._get_id_pfantmol()
        if id_ is not None:
            row = self._f.query_pfantmol(**{"pfantmol.id": id_}).fetchone()
            for fieldname, e in self._edit_map_pfantmol.items():
                v = row[fieldname]
                e.setText(str(v) if v is not None else "")

    def _fill_edits_statel(self):
        id_ = self._get_id_statel()
        if id_ is not None:
            row = self._f.query_state(**{"state.id": id_}).fetchone()
            for fieldname, e in self._edit_map_statel.items():
                v = row[fieldname]
                e.setText(str(v) if v is not None else "")

    def _fill_edits_state2l(self):
        id_ = self._get_id_state2l()
        if id_ is not None:
            row = self._f.query_state(**{"state.id": id_}).fetchone()
            for fieldname, e in self._edit_map_state2l.items():
                v = row[fieldname]
                e.setText(str(v) if v is not None else "")


    def _fill_edits_system(self):
        id_ = self._get_id_system()
        if id_ is not None:
            row = self._f.query_system(**{"system.id": id_}).fetchone()
            for fieldname, e in self._edit_map_system.items():
                v = row[fieldname]
                e.setText(str(v) if v is not None else "")

    def _update_label_fcf(self):
        n, fcfs = 0, self._get_fcfs()
        if fcfs is not None:
            n = len(fcfs)
        s = '<font color="{}">Franck-Condon Factors (FCFs) for {} vibrational transition{}</font>'.\
            format("blue" if n != 0 else "red", n, "" if n == 1 else "s")
        self.label_fcf.setText(s)

