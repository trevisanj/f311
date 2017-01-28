"""Represents SQLite database of molecular constants"""

import a99
from .. import FileSQLiteDB
import tabulate


__all__ = ["FileHitranDB"]

#
# __fileobj = None
# def get_conn():
#     return a99.get_conn(__ALIAS)


class FileHitranDB(FileSQLiteDB):
    description = "HITRAN Molecules Catalogue"
    default_filename = "hitrandb.sqlite"
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
        c.execute("""create table molecule (ID integer unique, Formula text unique, Name text)""")
        # **Note** isotopologue.ID is not unique, it starts over for each molecule
        c.execute("""create table isotopologue (ID integer,
                                                ID_molecule integer,
                                                Formula text unique,
                                                AFGL_Code integer,
                                                Abundance real
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
        sql = """select * from molecule{} order by ID""".format(where)
        r = conn.execute(sql, list(kwargs.values()))
        return r

    def query_isotopologue(self, **kwargs):
        """Convenience function to query 'isotopologue' table

        Args, Returns: see query_molecule

        Example:

        >>> f = FileHitranDB()
        >>> f.init_default()
        >>> _ = f.query_isotopologue(**{"molecule.formula": "OH"})
        """
        where = ""
        if len(kwargs) > 0:
            where = " where " + " and ".join([key + " = ?" for key in kwargs])
        conn = self.get_conn()
        sql = """select molecule.formula as m_formula, isotopologue.* from isotopologue
                 join molecule on isotopologue.id_molecule = molecule.id{}""".format(where)
        r = conn.execute(sql, list(kwargs.values()))
        return r

    def print_isotopologues(self, **kwargs):
        """
        Prints isotopologues table in console

        Args:
            **kwargs: arguments passed to query_state()

        Example:

        >>> f = FileHitranDB()
        >>> f.init_default()
        >>> f.print_isotopologues(**{"molecule.formula": "CO"})
        """
        r = self.query_isotopologue(**kwargs)
        data, header = a99.cursor_to_data_header(r)
        print(tabulate.tabulate(data, header))
