"""
Class Catalog -- resources to retrieve File* classes by different criteria
"""

from collections import OrderedDict
# from .. import filetypes as ft
import importlib
import a99

__all__ = [
    "classes_txt", "classes_bin", "classes_sp", "classes_file", "classes_collection",
    "get_suitable_vis_classes", "get_suitable_vis_list_classes"
    ]


def get_suitable_vis_classes(obj):
    """Retuns a list of Vis classes that can handle obj."""

    ret = []
    for class_ in classes_vis():
        if isinstance(obj, class_.input_classes):
            ret.append(class_)
    return ret


def get_suitable_vis_list_classes(objs):
    """Retuns a list of VisList classes that can handle a list of objects."""

    from f311 import explorer as ex

    ret = []
    for class_ in classes_vis():
        if isinstance(class_, ex.VisList):
            flag_can = True
            for obj in objs:
                if not isinstance(obj, class_.item_input_classes):
                    flag_can = False
                    break
            if flag_can:
                ret.append(class_)
    return ret


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


def classes_vis():
    """All known Vis* classes"""
    if __flag_first:
        __setup()
    return _classes_vis


def _collect_classes(m):
    """
    Adds entries to _classes_*

    Args:
        m: module object that must contain the following sub-modules: datatypes, vis
    """
    from f311 import filetypes as ft
    from f311 import explorer as ex

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
    # All kwnown Vis* classes

    _extend(_classes_vis, a99.get_classes_in_module(m, ex.Vis))


# # List of classes representing all file formats either read or written
#   ====================================================================
_classes_txt = []
_classes_bin = []
_classes_sp = []
_classes_file = []
_classes_vis = []
__flag_first = True
__collaborators = OrderedDict()  # (("f311.filetypes",  f311.filetypes),))


def __setup():
    """Will be executed in the first time someone calls classes_*() """
    global __collaborators, __flag_first
    __flag_first = False
    for pkgname in COLLABORATORS:
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
