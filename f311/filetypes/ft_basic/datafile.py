"""
Ancestor class for all classes that represent an input file.
"""


import a99
import os

__all__ = ["DataFile"]


class DataFile(a99.AttrsPart):
    """
    Class representing a file in disk

    Inheriting this class:
      - implement _do_load() if you want to make it loadable
      - implement _do_save() if you would like to make it saveable
      - implement some filetype check, either inheriting _test_magic() or within _do_load().
        This is optional, but **strongly advised**, because this will lower the chance that the
        automatic loader (see load_with_classes()) detects a wrong file type
    """
    # Description, e.g. "main configuration"
    # TODO investigate further, I think this attribute did not succeed
    description = ""
    # Descendants shoulds set this
    default_filename = None
    # Whether it is a text file format (otherwise binary)
    flag_txt = True
    # Whether or not to be considered by load_any_file()
    flag_collect = True
    # List of script names that can edit this file type
    editors = None

    def __init__(self):
        a99.AttrsPart.__init__(self)
        # File name is set by load()
        self.__flag_loaded = False
        self.filename = None

    # # Methods to be implemented by subclasses
    #   =======================================

    def _do_save_as(self, filename):
        raise NotImplementedError()

    def _do_load(self, filename):
        raise NotImplementedError("Forgot to implement _do_load() for class '{}'".
                                  format(self.classname))

    def _test_magic(self, filename):
        """Opens file just to verify whether it is what it is expected to be

        Implement this if you want to implement file type verification separate from _do_load()
        """
        pass

    # # Interface
    #   =========

    def save_as(self, filename=None):
        """
        Dumps object contents into file on disk.

        Args:
          filename (optional): defaults to self.filename. If passed, self.filename
            will be updated to filename.
        """
        if filename is None:
            filename = self.filename
        if filename is None:
            filename = self.default_filename
        self._do_save_as(filename)
        self.filename = filename

    def load(self, filename=None):
        """Loads file and registers filename as attribute."""
        assert not self.__flag_loaded, "File can be loaded only once"
        if filename is None:
            filename = self.default_filename
        assert filename is not None, \
            "{0!s} class has no default filename".format(self.__class__.__name__)

        # Convention: trying to open empty file is an error,
        # because it could be of (almost) any type.

        size = os.path.getsize(filename)
        if size == 0:
            raise RuntimeError("Empty file: '{0!s}'".format(filename))

        self._test_magic(filename)
        self._do_load(filename)
        self.filename = filename
        self.__flag_loaded = True

    def init_default(self):
        """
        Initializes object with its default values

        Tries to load self.default_filename from default
        data directory. For safety, filename is reset to None so that it doesn't point to the
        original file.
        """
        from f311 import filetypes as ft
        if self.default_filename is None:
            raise RuntimeError("Class '{}' has no default filename".format(self.__class__.__name__))
        fullpath = ft.get_default_data_path(self.default_filename, module=ft)
        self.load(fullpath)
        self.filename = None

