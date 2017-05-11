
from collections import OrderedDict
import sqlite3
from .datafile import DataFile
import a99
#from ... import filetypes as ft
import shutil
import os


__all__ = ["FileSQLiteDB"]


class FileSQLiteDB(DataFile):
    """Represents a SQLite database file.

    This class is not supposed to be instantialized. It serves as an ancestor for other classes
    that implement specific database schemas."""

    attrs = ["classname", "filename", "tables"]
    flag_txt = False

    # (xgear info): {(table name): {(field name): [caption, description], ...}, ...}
    #
    #  See ftpyfant.convmol.moldb for example
    gui_info = {}

    @property
    def tables(self):
        """Return a list of the database table names"""
        return self._get_table_names()

    def __init__(self, *args):
        DataFile.__init__(self, *args)
        self._conn = None

    # # Abstract
    #   ========

    def _create_schema(self):
        """Responsible for executing the CREATE TABLE statements

        Does not actually raise. If you don't want a schema, that's fine"""
        pass

    def _populate(self):
        """Responsible for that initial kick to a DB with all tables created, but empty

        Does not actually raise. If you don't want to populate the database, that's fine"""
        pass

    # # Override
    #   ========

    def init_default(self):
        """Overriden to take default database and save locally

        The issue was that init_default() sets self.filename to None; however there can be no
        SQLite database without a corresponding file (not using *memory* here)

        Should not keep default file open either (as it is in the API directory and shouldn't be
        messed by user)
        """
        from f311 import filetypes as ft
        if self.default_filename is None:
            raise RuntimeError("Class '{}' has no default filename".format(self.__class__.__name__))
        fullpath = ft.get_default_data_path(self.default_filename, class_=self.__class__)
        self.load(fullpath)
        name, ext = os.path.splitext(self.default_filename)
        new = a99.new_filename(os.path.join("./", name), ext)
        self.save_as(new)

    def _do_load(self, filename):
        """Loading here is limited to opening a connection"""
        self.__get_conn(filename=filename)
        self._get_table_names()  # tests if it is really a database

    def _do_save_as(self, filename):
        """Closes connection, copies DB file, and opens again pointing to new file

        **Note** if filename equals current filename, does nothing!
        """
        if filename != self.filename:
            self._ensure_filename()
            self._close_if_open()
            shutil.copyfile(self.filename, filename)
            self.__get_conn(filename=filename)

    def _close_if_open(self):
        if self._conn_is_open():
            self._conn.close()
            self._conn = None

    def _ensure_filename(self):
        if self.filename is None:
            raise RuntimeError("'filename' attribute is not set")

    # # Interface
    #   =========

    def _get_table_names(self):
        return a99.get_table_names(self.__get_conn())

    def delete(self):
        """Removes .sqlite file. **CAREFUL** needless say"""
        self._ensure_filename()
        self._close_if_open()
        os.remove(self.filename)

    def create_schema(self):
        """Creates database schema"""
        self._ensure_filename()
        self._create_schema()

    def populate(self):
        """Series of INSERT statements to populate database with its initial contents"""
        self._ensure_filename()
        self._populate()

    def get_conn(self, flag_force_new=False):
        """Returns sqlite3.Connection object with a non-default row factory.

        Args:
            flag_force_new: returns a new connection irrespective of one already being open.
                            Does **not** close existing open connection

        """
        self._ensure_filename()
        return self.__get_conn(flag_force_new)

    def get_table_info(self, tablename):
        """Returns information about fields of a specific table

        Returns:  dict of MyDBRow indexed by field name

        **Note** Fields "caption" and "tooltip" are added to rows using information in moldb.gui_info

        """
        conn = self.__get_conn()
        ret = a99.get_table_info(conn, tablename)

        if len(ret) == 0:
            raise RuntimeError("Cannot get info for table '{}'".format(tablename))

        more = self.gui_info.get(tablename)
        for row in ret.values():
            caption, tooltip = None, None
            if more:
                info = more.get(row["name"])
                if info:
                    caption, tooltip = info
            row["caption"] = caption
            row["tooltip"] = tooltip

        return ret

    # # Internal gear
    #   =============

    def _conn_is_open(self):
        """Tests sqlite3 connection, returns T/F"""
        return a99.conn_is_open(self._conn)

    def __get_conn(self, flag_force_new=False, filename=None):
        """Returns connection to database. Tries to return existing connection, unless flag_force_new

        Args:
            flag_force_new:
            filename:

        Returns: sqlite3.Connection object

        **Note** this is a private method because you can get a connection to any file, so it has to
                 be used in the right moment
        """
        flag_open_new = flag_force_new or not self._conn_is_open()

        if flag_open_new:
            if filename is None:
                filename = self.filename
            conn = a99.get_conn(filename)
            self._conn = conn
        else:
            conn = self._conn
        return conn
