import a99
from .. import FileSQLiteDB
import tabulate


__all__ = ["FileHitranDB"]

#
# __fileobj = None
# def get_conn():
#     return a99.get_conn(__ALIAS)


class FileHitranDB(FileSQLiteDB):
    """HITRAN Molecules Catalogue"""

    default_filename = "hitrandb.sqlite"

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
