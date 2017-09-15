"""
Represents SQLite database of molecular constants



"""

import a99
from .. import FileSQLiteDB
# import sqlite3
import tabulate
import re
import os



__all__ = ["FileMolDB", "SPDF", "GREEK_SPDF", "MolConsts", "some_mol_consts", "MolConstPopulateError",
           "mol_consts_to_system_str", "SPDF_to_int", "int_to_SPDF"]

#
# __fileobj = None
# def get_conn():
#     return a99.get_conn(__ALIAS)

SPDF = ["Σ", "Π", "Δ", "Φ"]
GREEK_SPDF = SPDF

# superscript numbers
_conv_sup = {1: "\u2071",
             2: "\u00b2",
             3: "\u00b3",
             4: "\u2074"}


class FileMolDB(FileSQLiteDB):
    description = "Database of Molecular Constants"
    default_filename = "moldb.sqlite"
    editors = ["convmol.py"]
    gui_info = {
        "molecule": {
            "formula": [None, "formula of molecule, <i>e.g.</i>, 'OH'"],
        },
        "pfantmol": {
            'description': [None, "free text"],
            "fe": [None, "oscillator strength"],
            "do": [None, "dissociation constant (eV)"],
            "am": [None, "mass of first element"],
            "bm": [None, "mass of second element"],
            "ua": [None, "value of partition function for first element"],
            "ub": [None, "value of partition function for second element"],
            "te": [None, "electronic term"],
            "cro": [None, "delta Kronecker (0: sigma transitions; 1: non-Sigma transitions)"],
            "s": [None, "?doc?"]
        },
        "state": {
        "omega_e": ["ω<sub>e</sub>", "vibrational constant – first term (cm<sup>-1</sup>)"],
        "omega_ex_e": ["ω<sub>e</sub>x<sub>e</sub>", "vibrational constant – second term (cm<sup>-1</sup>)"],
        "omega_ey_e": ["ω<sub>e</sub>y<sub>e</sub>", " vibrational constant – third term (cm<sup>-1</sup>)"],
        "B_e": ["B<sub>e</sub>", "rotational constant in equilibrium position (cm<sup>-1</sup>)"],
        "alpha_e": ["α<sub>e</sub>", "rotational constant – first term (cm<sup>-1</sup>)"],
        "D_e": ["D<sub>e</sub>", "centrifugal distortion constant (cm<sup>-1</sup>)"],
        "beta_e": ["β<sub>e</sub>", "rotational constant – first term, centrifugal force (cm<sup>-1</sup>)"],
        "A": [None, "Coupling counstant (cm<sup>-1</sup>)"],
          },
        "system": {
            "from_label": ["State'", None],
            "from_spdf": ["Λ'", "0/1/2/3 meaning Σ/Π/Δ/Φ"],
            "to_label": ['State"', None],
            "to_spdf": ['Λ"', "0/1/2/3 meaning Σ/Π/Δ/Φ"]
        }

    }

    @staticmethod
    def get_system_short(row):
        """Converts a 'system' row to its superscript and Greek letters notation"""
        return _format_system(row)

    # TODO see if this is still used, perhaps now only MolConsts.populate_from_db()
    def get_mol_consts(self, id_pfantmol, id_state, id_system):
        """Returns dict-like with field values from tables 'molecule', 'state', 'pfantmol', 'system'"""
        conn = self.get_conn()
        ret = conn.execute("select * from pfantmol where id = ?", (id_pfantmol,)).fetchone()
        ret.update(conn.execute("select * from state where id = ?", (id_state,)).fetchone())
        ret.update(conn.execute("select * from system where id = ?", (id_system,)).fetchone())
        ret.update(conn.execute("select * from molecule where id = ?", (ret["id_molecule"],)).fetchone())
        return ret

    def query_molecule(self, **kwargs):
        """Convenience function to query 'molecule' table

        Args:
            **kwargs: filter fieldname=value pairs to be passed to WHERE clause

        Returns: sqlite3 cursor
        """
        where = ""
        if len(kwargs) > 0:
            where = " where " + " and ".join([key + " = ?" for key in kwargs])
        conn = self.get_conn()
        sql = """select * from molecule{} order by formula""".format(where)
        r = conn.execute(sql, list(kwargs.values()))
        return r

    def query_state(self, **kwargs):
        """Convenience function to query 'state' table (joins with table molecule)

        Args, Returns: see query_molecule
        """
        where = ""
        if len(kwargs) > 0:
            where = " where " + " and ".join([key + " = ?" for key in kwargs])
        conn = self.get_conn()
        sql = """select molecule.formula, state.* from state
                 join molecule on state.id_molecule = molecule.id{}""".format(where)
        r = conn.execute(sql, list(kwargs.values()))
        return r

    def query_pfantmol(self, **kwargs):
        """Convenience function to query 'pfantmol' table (joins with table molecule)

        Args, Returns: see query_molecule
        """
        where = ""
        if len(kwargs) > 0:
            where = " where " + " and ".join([key + " = ?" for key in kwargs])
        conn = self.get_conn()
        sql = """select molecule.formula, pfantmol.* from pfantmol
                 join molecule on pfantmol.id_molecule = molecule.id{}""".format(where)
        r = conn.execute(sql, list(kwargs.values()))
        return r

    def query_system(self, **kwargs):
        """Convenience function to query 'system' table (joins with table molecule)

        Args, Returns: see query_molecule
        """
        where = ""
        if len(kwargs) > 0:
            where = " where " + " and ".join([key + " = ?" for key in kwargs])
        conn = self.get_conn()
        sql = """select molecule.formula, system.* from system
                 join molecule on system.id_molecule = molecule.id{}""".format(where)
        r = conn.execute(sql, list(kwargs.values()))
        return r

    def query_fcf(self, **kwargs):
        """Convenience function to query 'fcf' table

        Args, Returns: see query_molecule
        """
        where = ""
        if len(kwargs) > 0:
            where = " where " + " and ".join([key + " = ?" for key in kwargs])
        conn = self.get_conn()
        sql = """select * from fcf{} order by vl, v2l""".format(where)
        r = conn.execute(sql, list(kwargs.values()))
        return r

    def test_query_state(self):
        """
        Test function

        Example:

        >>> f = FileMolDB()
        >>> f.init_default()
        >>> conn = f.get_conn()
        >>> cursor = conn.execute("select * from state where id = 10")
        >>> row = cursor.fetchone()
        >>> print(row)
        MyDBRow([('id', 10), ('id_molecule', 2), ('State', 'F ⁱPi_u'), ('T_e', 75456.9), ('omega_e', 1557.5), ('omega_ex_e', None), ('omega_ey_e', None), ('B_e', 1.645), ('alpha_e', 0.019), ('gamma_e', None), ('D_e', 6e-06), ('beta_e', None), ('r_e', 1.307), ('Trans', 'F ← X R'), ('nu_00', 74532.9)])
        """

    def print_states(self, **kwargs):
        """
        Prints states table in console

        Args:
            **kwargs: arguments passed to query_state()

        Example:

        >>> f = FileMolDB()
        >>> f.init_default()
        >>> f.print_states(formula="OH")
        """
        r = self.query_state(**kwargs)
        data, header0 = a99.cursor_to_data_header(r)

        # ti = a99.get_table_info(_ALIAS, "state")
        # header = [(ti[name]["caption"] or name) if ti.get(name) else name for name in header0]

        header = header0

        print(tabulate.tabulate(data, header))

    def get_transition_dict(self):
        """
        Generates a dictionary where (molecule, state_from, state_to) can be searched to retrieve state rows

        """
        rm = self.query_molecule()
        ret = {}
        for row_molecule in rm:
            rs = self.query_state(id_molecule=row_molecule["id"])
            for row_state in rs:
                row_state.None_to_zero()

                trans_ = row_state["Trans"]
                if trans_ is None or trans_ == 0:
                    continue
                keys = self._formula_trans_to_tuples(row_molecule["formula"], trans_)

                if keys is None:
                    continue
                for key in keys:
                    ret[key] = row_state
        return ret

    def get_fcf_dict(self, id_system):
        """Returns a dictionary indexed by (vl, v2l) and FCFs as values"""

        _ret = self.query_fcf(id_system=id_system).fetchall()
        ret = {}
        for r in _ret:
            ret[(r["vl"], r["v2l"])] = r["value"]
        return ret

    def find_id_system(self, mol_consts):
        """Returns id_system or None"""

        ff = ["from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf"]
        one = self.get_conn().execute("select id from system where id_molecule = ? and "+
                           " and ".join(["{} = ?".format(x) for x in ff]),
                           [mol_consts["id_molecule"]]+[mol_consts[x] for x in ff]).fetchone()
        if one is None:
            return None
        return one["id"]



    def insert_system_if_does_not_exist(self, mol_consts, comments=""):
        """
        Inserts system if does not exist yet

        Args:
            mol_consts: a MolConsts
            comments: table system.comments value, in case of new record
        """

        id_ = self.find_id_system(mol_consts)

        if id_ is not None:
            return id_

        ff = ("id_molecule", "from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf")
        values = [mol_consts[x] for x in ff]+[comments]
        ff.append("comments")
        cursor = conn.execute("""insert into system ({}) values ({})""".format(", ".join(ff),
            ", ".join(["?"]*len(ff))), values)
        id_ = cursor.lastrowid
        return id_


    def _create_schema(self):
        conn = self.get_conn()
        c = conn.cursor()
        # TODO revisit each of these variables and see
        # TODO where they are used in PFANT
        # TODO what they are
        # TODO if they repeat somewhere
        c.execute("""create table molecule (id integer primary key,
                                            formula text unique,
                                            name text
                                           )""")


        # I decided that I won't try to track down all the Physics to determine which of the
        # molecule-wide "constants" in PFANT molecular lines file (e.g. 'molecules.dat') are
        # dependent on the molecule, a (vl, v2l) transition thereof etc.
        #
        # Instead, it seems to be historically sensible to reproduce the structure found in that
        # file, i.e., create a table with the same fields found in the molecule header of the PFANT
        # molecular lines file (e.g. 'molecules.dat'), **no less, no more**
        #
        # **Note** 'symbol_a', 'symbol_b' matches element symbols found in 'dissoc.dat'
        c.execute("""create table pfantmol (id integer primary key,
                                            id_molecule integer,
                                            description text,
                                            fe real,
                                            do real,
                                            am real,
                                            bm real,
                                            ua real,
                                            ub real,
                                            te real,
                                            cro real,
                                            s real,
                                            comments text
                                           )""")

        # This "state" information comes from NIST Chemistry Web Book.
        #
        # The field names are exactly as extracted from the header rows of the tables of diatomic
        # molecular constants in that book
        #
        c.execute("""create table state (id integer primary key,
                                         id_molecule integer,
                                         State text,
                                         T_e real,
                                         omega_e real,
                                         omega_ex_e real,
                                         omega_ey_e real,
                                         B_e real,
                                         alpha_e real,
                                         gamma_e real,
                                         D_e real,
                                         beta_e real,
                                         r_e real,
                                         Trans text,
                                         nu_00 real,
                                         A real,
                                         comments text
                                        )""")
                                         # s_label text,
                                         # s_multiplicity integer,
                                         # s_spdf integer,
                                         # s_parity text


        # A     2            Sigma
        # label multiplicity spdf
        #
        # spdf:
        #     Sigma: 0
        #     Pi: 1
        #     Delta: 2
        #     Phi: 3
        c.execute("""create table system
                     (id integer primary key,
                      id_molecule integer,
                      from_label text,
                      from_mult integer,
                      from_spdf integer,
                      to_label text,
                      to_mult integer,
                      to_spdf integer,
                      comments text
                      )""")

        # Franck-Condon Factors table
        #
        # Something that I noticed from Bruno Castilho's directory at ATMOS/wrk4/Mole: both CH and
        # 13CH use the same Franck-Condon factors (files 'sjalist.txt', 'sjblist.txt' etc).
        # Therefore, the 'fcf' table below have a N-1 relation to table 'system', not to table
        # 'pfantmol' (the latter is where there is a distinction between 13CH and CH)
        #
        c.execute("""create table fcf (id integer primary key,
                                       id_system integer,
                                       vl integer,
                                       v2l integer,
                                       value real,
                                       comments text
                                       )""")

        conn.commit()
        conn.close()

    @staticmethod
    def _formula_trans_to_tuples(formula, trans):
        """Generates several tuples (formula, state_from, state_to)

        Args:
            formula: chemical formula, such as "TiO". This must be the same formula found in a
                     the 'molecule' table
            trans: string such as "A ↔ X R", "D ← X R", "B → A R"

        Returns: list of tuples [(formula, state_from, state_to), ...]
                 Example:  [('TiO', 'A', 'B'), ('TiO', 'R', 'B')]

        """

        try:
            lr = [re.split(" ", x.strip()) for x in re.split("[↔←→]", trans)]
            if "→" in trans:
                from_ = lr[0]
                to = lr[1]
            elif "←" in trans:
                to = lr[0]
                from_ = lr[1]
            else:
                from_ = to = lr[0]+lr[1]

            pairs = [(f, t) for t in to for f in from_ if t != f]

            ret = [(formula,)+pair for pair in pairs]
        except IndexError:
            ret = None

        return ret



####################################################################################################
# old f311.physics.molconsts


_KEYS = ["fe", "bm", "te", "do", "ua", "cro", "am", "ub", "s",
         "from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf",
         "statel_omega_e", "statel_B_e", "statel_beta_e", "statel_omega_ex_e", "statel_alpha_e",
         "statel_A", "statel_omega_ey_e", "statel_D_e",
         "state2l_omega_e", "state2l_B_e", "state2l_beta_e", "state2l_omega_ex_e", "state2l_alpha_e",
         "state2l_A", "state2l_omega_ey_e", "state2l_D_e", "name", "formula",
         "id_molecule", "id_pfantmol", "id_system", "id_statel", "id_state2l"]


class MolConsts(dict):
    """Dict subclass that will hold several molecular constants

    The dictionary keys match field names in tables ("pfantmol", "state", "system") in a FileMolDB.
    Keys "statel_*" and "state2l_*" have these prefixes to indicate initial and final state.

    Methods populate_all_*() populates the dictionary completely.

    Methods populate_*() (where * does not start with "all") populates partially.
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        for key in _KEYS:
            self[key] = None

    def None_to_zero(self):
        """Replaces None values with zero"""

        for key in self:
            if self[key] is None:
                self[key] = 0.

    def populate_parse_str(self, string):
        """
        Populates (from_*) and (to_*) taking string as input

        String examples:

            "OH [A 2 Sigma - X 2 Pi]"

            "12C16O INFRARED [X 1 SIGMA+]"

        **Note** *_spdf case is ignored and converted to int

        **Note** If the SPDF has an additional "+"/"-", this will not be part of the SPDF.
                 For example, in the string "CH BX [B2SIGMA- - X2PI]", initial SPDF considered will
                 be "SIGMA", not "SIGMA-"
        """

        fieldnames = ["from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf"]
        transforms = [lambda x: x, lambda x: int(x), SPDF_to_int,
                      lambda x: x, lambda x: int(x), SPDF_to_int,]

        # Formula
        groups = re.match("\w+", string)
        if groups is not None:
            self["formula"] = groups[0]

        # Parses system
        expr = re.compile("\[\s*([a-zA-Z])\s*(\d+)\s*([a-zA-Z0-9]+)[+-]{0,1}\s*-+\s*\s*([a-zA-Z])\s*(\d+)\s*([a-zA-Z0-9]+)[+-]{0,1}\s*\]")
        groups = expr.search(string)
        if groups is not None:
            pieces = [groups[i] for i in range(1, 7)]
        else:
            # Initial and final state are the same. Example "12C16O INFRARED [X 1 SIGMA+]"
            expr = re.compile("\[\s*([a-zA-Z])\s*(\d+)\s*([a-zA-Z0-9]+)[+-]{0,1}\s*\]")

            groups = expr.search(string)
            if groups is not None:
                pieces = [groups[i] for i in range(1, 4)]*2

            if groups is None:
                raise ValueError("Could not understand str '{}'".format(string))

        self.update(zip(fieldnames, [f(piece) for f, piece in zip(transforms, pieces)]))

    def populate_all_using_str(self, db, string):
        self.populate_parse_str(string)
        self.populate_ids(db)
        self.populate_all_using_ids(db)

    def populate_all_using_ids(self, db, id_molecule=None, id_system=None, id_pfantmol=None,
                               id_statel=None, id_state2l=None):
        """
        Populates completely, given all necessary table ids

        Args:
            db: FileMolDB object
            id_molecule: id in table "molecule"
            id_system: id in table "system"
            id_pfantmol: id in table "pfantmol"
            id_statel: id in table "state" for the initial state
            id_state2l: id in table "state" for the final state

        Arguments id_* have a fallback, which is self[argument].


        """
        assert isinstance(db, FileMolDB)

        if id_molecule is None: id_molecule = self["id_molecule"]
        if id_system is None: id_system = self["id_system"]
        if id_pfantmol is None: id_pfantmol = self["id_pfantmol"]
        if id_statel is None: id_statel = self["id_statel"]
        if id_state2l is None: id_state2l = self["id_state2l"]

        # key name, id, table name, prefix for key in dictionary
        _map = [("id_molecule", id_molecule, "molecule", ""),
                ("id_system", id_system, "system", ""),
                ("id_pfantmol", id_pfantmol, "pfantmol", ""),
                ("id_statel", id_statel, "state", "statel_"),
                ("id_state2l", id_state2l, "state", "state2l_"),
                ]

        for keyname, id_, tablename, prefix in _map:
            if id_ is not None:
                ti = db.get_table_info(tablename)
                row = db.get_conn().execute("select * from {} where id = ?".format(tablename),
                                            (id_,)).fetchone()

                if row is None:
                    raise ValueError("Invalid {}: id {} does not exist in table '{}'".format(keyname, id_, tablename))

                for fieldname in ti:
                    if not fieldname.startswith("id"):
                        self[prefix + fieldname] = row[fieldname]

            self[keyname] = id_

    def populate_ids(self, db):
        """Populates (id_*) with values found using (molecule name) and (from_*) and (to_*)."""

        ff = ("id_molecule", "id_system", "id_pfantmol", "id_statel", "id_state2l")
        methods = (self._populate_id_molecule, self._populate_id_system,
                   self._populate_id_pfantmol, self._populate_ids_state)

        for f in ff:
            self[f] = None

        for m in methods:
            try:
                m(db)
            except MolConstPopulateError:
                pass

    def _populate_id_molecule(self, db):
        need = ("formula",)
        if any((self[x] is None for x in need)):
            raise MolConstPopulateError("I need ({})".format(", ".join(need)))

        one = db.get_conn().execute("select id from molecule where formula = ?",
                                    (self["formula"],)).fetchone()
        self["id_molecule"] = one["id"] if one is not None else None

    def _populate_id_system(self, db):
        need = ("id_molecule", "from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf")
        if any((self[x] is None for x in need)):
            raise MolConstPopulateError("I need ({})".format(", ".join(need)))
        self["id_system"] = db.find_id_system(self)

    def _populate_ids_state(self, db):
        """Populates id_statel and id_state2l"""

        need = ("id_molecule", "from_label", "to_label")
        if any((self[x] is None for x in need)):
            raise MolConstPopulateError("I need ({})".format(", ".join(need)))

        _map = [("from_label", "id_statel"), ("to_label", "id_state2l")]
        for fn_to_match, fn_dest in _map:
            one = db.get_conn().execute("select id from state where id_molecule = ? and "
                                        "State like \"{}%\"".format(self[fn_to_match]),
                                        (self["id_molecule"],)).fetchone()
            self[fn_dest] = one["id"] if one is not None else None

    def _populate_id_pfantmol(self, db):
        """Populates id_pfantmol using formula, to_*, and from_*"""

        need = ("formula", "from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf")
        if any((self[x] is None for x in need)):
            raise MolConstPopulateError("I need ({})".format(", ".join(need)))

        self["id_pfantmol"] = None

        # Will check match one by one. Will have to parse PFANT molecule descriptions.
        # **Note** currently not accounting for ambiguous match (always takes first match).
        #
        cursor = db.get_conn().execute("select * from pfantmol")
        for row in cursor:
            another = MolConsts()
            another.populate_parse_str(row["description"])

            found = True
            for field_name in need:
                if self[field_name] != another[field_name]:
                    found = False
                    break

            if found:
                self["id_pfantmol"] = row["id"]
                return


def some_mol_consts():
    """
    Returns a MolConsts object populated with 'OH A2Sigma-X2Pi' information

    **Note** Creates new moldb.xxxx.sqlite file every time it is run, then deletes it
    """

    db = FileMolDB()
    db.init_default()

    ret = MolConsts()
    ret.populate_all_using_ids(db, id_system=6, id_pfantmol=12, id_statel=96, id_state2l=97)

    # Finally deletes file
    db.get_conn().close()
    os.unlink(db.filename)

    return ret


class MolConstPopulateError(Exception):
    pass


_PLAIN = -1
_GREEK = 0


def mol_consts_to_system_str(mol_consts, style=_GREEK):
    """Compiles system information into string

    Args:
        mol_consts: dict-like containing the from_* and to_* values
        style: rendering style

    Returns:
        str
    """

    if style == _PLAIN:
        fmult = lambda x: x
        fspdf = lambda x: x
    elif style == _GREEK:
        fmult = lambda x: _conv_sup[x]
        fspdf = lambda x: SPDF[x]

    return "{}{}{} - {}{}{}".format(mol_consts["from_label"], fmult(mol_consts["from_mult"]),
                                    fspdf(mol_consts["from_spdf"]), mol_consts["to_label"],
                                    fmult(mol_consts["to_mult"]), fspdf(mol_consts["to_spdf"]))


_SPDF = ["SIGMA", "PI", "DELTA", "PHI"]
def SPDF_to_int(spdf):
    try:
        ret = _SPDF.index(spdf.upper())
    except ValueError:
        raise ValueError("Invalid SPDF: '{}' (possible values: {})".format(spdf.upper(), _SPDF))
    return ret

def int_to_SPDF(number):
    return SPDF[number]