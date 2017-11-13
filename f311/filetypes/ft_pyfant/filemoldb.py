"""
Represents SQLite database of molecular constants
"""

import a99
from .. import FileSQLiteDB
from .. import basic
# import sqlite3
import tabulate
import re
import os
import inspect

__all__ = ["FileMolDB"]

#
# __fileobj = None
# def get_conn():
#     return a99.get_conn(__ALIAS)



class FileMolDB(FileSQLiteDB):
    """Database of Molecular Constants"""
    default_filename = "moldb.sqlite"
    editors = ["convmol.py", "moldbed.py"]
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
            "cro": [None, "delta Kronecker (1: Sigma-Sigma transitions; 0: non-Sigma transitions)"],
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
        sql = """select * from pfantmol{}""".format(where)
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
        sql = """select * from system{}""".format(where)
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

    def find_id_system(self, molconsts):
        """Returns id_system or None"""

        ff = ["from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf"]
        one = self.get_conn().execute("select id from system where id_molecule = ? and "+
                           " and ".join(["{} = ?".format(x) for x in ff]),
                           [molconsts["id_molecule"]]+[molconsts[x] for x in ff]).fetchone()
        if one is None:
            return None
        return one["id"]



    def insert_system_if_does_not_exist(self, molconsts, notes=""):
        """
        Inserts system if does not exist yet

        Args:
            molconsts: a MolConsts
            notes: table system.notes value, in case of new record
        """
        ff = ["id_molecule", "from_label", "from_mult", "from_spdf", "to_label", "to_mult",
              "to_spdf"]

        molconsts._i_need(ff)  # stay friendly, MolConsts

        id_ = self.find_id_system(molconsts)

        if id_ is not None:
            return id_


        values = [molconsts[x] for x in ff]+[notes]
        ff.append("notes")
        conn = self.get_conn()
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
        #
        c.execute("""create table pfantmol (id integer primary key,
                                            id_system integer,
                                            description text,
                                            fe real,
                                            do real,
                                            am real,
                                            bm real,
                                            ua real,
                                            ub real,
                                            te real,
                                            cro real,
                                            notes text
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
                                         notes text
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
                      notes text
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
                                       notes text
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



