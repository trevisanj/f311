"""
Class Catalog -- resources to retrieve File* classes by different criteria
"""

from collections import OrderedDict
# from .. import filetypes as ft
import importlib
import a99

__all__ = [
    "classes_txt", "classes_bin", "classes_sp", "classes_file", "classes_collection"
    ]


__COLLABORATORS = ["f311.filetypes"]


# def collaborators():
#     """Returns a dictionary of packages scanned to populate _classes_*
#
#     Example: {"f311.filetypes": f311.filetypes, }
#     """
#     if __flag_first:
#         __setup()
#     return __collaborators


def classes_txt():
    """Classes to consider when attempts to load a text file (see load_any_file())"""
    if __flag_first:
        __setup()
    return _classes_txt


def classes_bin():
    """Classes to consider when attempts to load a binary file (see load_any_file())"""
    if __flag_first:
        __setup()
    return _classes_bin


def classes_sp():
    """Classes to consider when attempts to load a spectrum file (see load_spectrum())"""
    if __flag_first:
        __setup()
    return _classes_sp


def classes_file():
    """All known File* classes"""
    if __flag_first:
        __setup()
    return _classes_file


def classes_collection():
    """
    Returns list of File* classes that can be converted to a SpectrumCollection
    """
    from f311 import filetypes as ft
    return classes_sp() + [ft.FileSpectrumList, ft.FileSparseCube, ft.FileFullCube]


def _collect_classes(m):
    """
    Adds entries to _classes_*

    Args:
        m: module object that must contain the following sub-modules: datatypes, vis
    """
    from f311 import filetypes as ft

    def _extend(classes, newclasses):
        """Filters out classes already present in list.

        This shouldn't be necessary, but collaborators may accidentally import already loaded
        classes into the datatypes namespace"""
        classes.extend([class_ for class_ in newclasses if class_ not in classes])
        # classes.extend(newclasses)

    file_classes = [class_ for class_ in a99.get_classes_in_module(m, ft.DataFile) if class_.flag_collect]

    # Classes to consider when attempts to load a text file (see load_any_file())
    _extend(_classes_txt, [class_ for class_ in file_classes if class_.flag_txt])

    # Classes to consider when attempts to load a binary file (see load_any_file())
    _extend(_classes_bin, [class_ for class_ in file_classes if not class_.flag_txt])
    # Adds Classes to consider when attempts to load a spectrum file (see load_spectrum())
    _extend(_classes_sp, [class_ for class_ in file_classes if issubclass(class_, ft.FileSpectrum)])
    # All kwown File* classes
    _extend(_classes_file, file_classes)


# # List of classes representing all file formats either read or written
#   ====================================================================
_classes_txt = []
_classes_bin = []
_classes_sp = []
_classes_file = []
__flag_first = True
__collaborators = OrderedDict()  # (("f311.filetypes",  f311.filetypes),))


def __setup():
    """Will be executed in the first time someone calls classes_*() """
    global __collaborators, __flag_first
    __flag_first = False
    for pkgname in __COLLABORATORS:
        try:
            pkg = importlib.import_module(pkgname)
            a99.get_python_logger().info("Imported collaborator package '{}'".format(pkgname))

            try:
                if hasattr(pkg, "_setup_filetypes"):
                    pkg._setup_filetypes()
                else:
                    _collect_classes(pkg)

                __collaborators[pkgname] = pkg
            except:
                a99.get_python_logger().exception(
                    "Actually, package '{}' gave error".format(pkgname))
                raise
        except:
            a99.get_python_logger().warning("Failed to import package '{}".format(pkgname))
            pass
