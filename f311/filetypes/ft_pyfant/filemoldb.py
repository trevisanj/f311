"""Represents SQLite database of molecular constants"""

import a99
from .. import FileSQLiteDB
# import sqlite3
import tabulate


__all__ = ["FileMolDB"]

#
# __fileobj = None
# def get_conn():
#     return a99.get_conn(__ALIAS)


class FileMolDB(FileSQLiteDB):
    description = "Database of Molecular Constants"
    default_filename = "moldb.sqlite"
    gui_data = {
        "molecule": {
            "name": [None, "name of molecule, <i>e.g.</i>, 'OH'"],
            "symbol_a": ["Symbol A", "symbol of first element"],
            "symbol_b": ["Symbol B", "symbol of second element"],
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
      }
    }

    def _create_schema(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("""create table molecule (id integer primary key,
                                            formula text unique,
                                            name text,
                                            symbol_a text,
                                            symbol_b text,
                                            fe real,
                                            do real,
                                            am real,
                                            bm real,
                                            ua real,
                                            ub real,
                                            te real,
                                            cro real,
                                            s real
                                           )""")
        # Note that it has no primary key
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
                                         s_label text,
                                         s_multiplicity integer,
                                         s_spdf integer,
                                         s_parity text,

                                        )""")

        conn.commit()
        conn.close()



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
        """Convenience function to query 'state' table

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
