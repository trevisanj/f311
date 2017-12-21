import sys
import os
import shutil

__all__ = ["get_default_data_path", "copy_default_data_file"]


def get_default_data_path(*args, module=None, class_=None, flag_raise=True):
    """
    Returns path to default data directory

    Arguments 'module' and 'class' give the chance to return path relative to package other than
    f311.filetypes

    Args:
        module: Python module object. It is expected that this module has a sub-subdirectory
                named 'data/default'
        class_: Python class object to extract path information from. If this argument is used,
                it will be expected that the class "root" package will have a sub-subdirectory
                named 'data/default'. Argument 'class_' **has precedence over argument 'module'**
        flag_raise: raises error if file is not found. This can be turned off for whichever purpose
    """
    if module is None:
        module = __get_filetypes_module()

    if class_ is not None:
        pkgname =  class_.__module__
        mseq = pkgname.split(".")
        if len(mseq) < 2 or mseq[1] != "filetypes":
            raise ValueError("Invalid module name for class '{}': '{}' "
                             "(must be '(...).filetypes[.(...)]')".format(class_.__name__, pkgname))
        # gets "root" module object
        # For example, if pkgname is "pyfant.filetypes.filemain", module below will be
        # the "pyfant" module object
        module = sys.modules[mseq[0]]
    module_path = os.path.split(module.__file__)[0]
    p = os.path.abspath(os.path.join(module_path, "data", "default", *args))

    if flag_raise:
        if not os.path.isfile(p):
            raise RuntimeError("Path not found '{}'".format(p))

    return p


def copy_default_data_file(filename, module=None):
    """Copies file from default data directory to local directory."""
    if module is None:
        module = __get_filetypes_module()
    fullpath = get_default_data_path(filename, module=module)
    shutil.copy(fullpath, ".")


def __get_filetypes_module():
    from f311 import filetypes as ft
    return ft

