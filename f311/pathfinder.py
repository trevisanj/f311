import sys
import os
import shutil

__all__ = ["get_default_data_path", "copy_default_data_file"]


def get_default_data_path(*args, module=None, class_=None):
    """
    Returns path to default data directory

    Arguments 'module' and 'class' give the chance to return path relative to package other than
    f311.filetypes

    Args:
        module: Python module object. It is expected that this module has a sub-subdirectory
                named 'data/default'
        class_: Python class object to extract path information from. If this argument is used,
                it will be expected that the class "root" package will have a subpackage called
                'filetypes', i.e., '(some package).filetypes'.
                **Has precedence over 'module' argument**

    """
    if module is None:
        module = __get_filetypes_module()

    if class_ is not None:
        pkgname =  class_.__module__
        mseq = pkgname.split(".")
        if len(mseq) < 2 or mseq[1] != "filetypes":
            raise ValueError("Invalid module name for class '{}': '{}' "
                             "(must be '(...).filetypes[.(...)]')".format(class_.__name__, pkgname))
        module = sys.modules[".".join(mseq[:2])]
    module_path = os.path.split(module.__file__)[0]
    p = os.path.abspath(os.path.join(module_path, "data", "default", *args))
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

