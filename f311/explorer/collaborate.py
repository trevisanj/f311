"""
"Collaboration" with other packages

"Collaborator" packages should have a method '_setup_astroapi()',
which adds entries to the _* variables in this module
"""


from collections import OrderedDict
import f311.filetypes as ft
from .. import explorer as ex
import importlib
import a99

__all__ = [
    "classes_txt", "classes_bin", "classes_sp", "classes_file", "classes_vis", "collaborators",
    "get_suitable_vis_classes", "get_class_package", "classes_collection"
    ]


# __all__ = [
#     "_classes_txt", "_classes_bin", "_classes_sp", "_classes_file", "_classes_vis",
#     "classes_txt", "classes_bin", "classes_sp", "classes_file", "classes_vis", "collaborators",
#     "get_suitable_vis_classes", "get_class_package", "classes_collection"
#     ]


def get_suitable_vis_classes(obj):
    """Retuns a list of Vis classes that can handle obj."""

    ret = []
    for class_ in classes_vis():
        if isinstance(obj, class_.input_classes):
            ret.append(class_)
    return ret


def get_suitable_vis_list_classes(objs):
    """Retuns a list of VisList classes that can handle a list of objects."""

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



def get_class_package(class_):
    """
    Returns package that class belongs to

    **Note** package must in hypydrive.collaborators, otherwise will raise
    """
    if __flag_first:
        __setup_collaboration()
    root_pkg_name = class_.__module__.split(".")[0]
    if root_pkg_name == a99.__name__:
        return a99
    if root_pkg_name not in __collaborators:
        raise RuntimeError("Class '{}' belongs to package '{}', "
                           "but the latter is not among hypydrive collaborators".
                           format(class_.__name__, root_pkg_name))
    return __collaborators[root_pkg_name]


def collaborators():
    if __flag_first:
        __setup_collaboration()
    return __collaborators

def _collect_classes(m):
    """
    Adds entries to _classes_*

    Args:
        m -- module object that must contain the following sub-modules: datatypes, vis
    """

    def _extend(classes, newclasses):
        """Filters out classes already present in list.

        This shouldn't be necessary, but collaborators may accidentally import already loaded
        classes into the datatypes namespace"""
        classes.extend([class_ for class_ in newclasses if class_ not in classes])
        # classes.extend(newclasses)

    file_classes = a99.get_classes_in_module(m, ft.DataFile)

    # Classes to consider when attempts to load a text file (see hypydrive.load_any_file())
    _extend(_classes_txt, [class_ for class_ in file_classes if class_.flag_txt])

    # Classes to consider when attempts to load a binary file (see hypydrive.load_any_file())
    _extend(_classes_bin, [class_ for class_ in file_classes if not class_.flag_txt])
    # Adds Classes to consider when attempts to load a spectrum file (see hypydrive.load_spectrum())
    _extend(_classes_sp, [class_ for class_ in file_classes if issubclass(class_, ft.FileSpectrum)])
    # All kwown File* classes
    _extend(_classes_file, file_classes)
    # All kwnown Vis* classes
    _extend(_classes_vis, a99.get_classes_in_module(m, ex.Vis))


# # List of classes representing all file formats either read or written
#   ====================================================================
# # Classes to consider when attempts to load a text file (see load_any_file())
# _classes_txt = [FileSpectrumNulbad, FileSpectrumPfant, FileSpectrumXY, FileOpa, FileModTxt]
# # Classes to consider when attempts to load a binary file (see load_any_file())
# _classes_bin = [FileModBin, FileSpectrumFits, FileMoo]
# # Classes to consider when attempts to load a spectrum file (see load_spectrum())
# _classes_sp = [FileSpectrumNulbad, FileSpectrumPfant, FileSpectrumXY, FileSpectrumFits]
# # All known File* classes
# _classes_file = get_classes_in_module(datatypes, DataFile)
# # All known Vis* classes
# _classes_vis = get_classes_in_module(vis, Vis)

_classes_txt = []
_classes_bin = []
_classes_sp = []
_classes_file = []
_classes_vis = []

__flag_first = True

def classes_txt():
    if __flag_first:
        __setup_collaboration()
    return _classes_txt


def classes_bin():
    if __flag_first:
        __setup_collaboration()
    return _classes_bin


def classes_sp():
    if __flag_first:
        __setup_collaboration()
    return _classes_sp


def classes_file():
    if __flag_first:
        __setup_collaboration()
    return _classes_file


def classes_vis():
    if __flag_first:
        __setup_collaboration()
    return _classes_vis


def classes_collection():
    """
    Returns list of File* classes that can be converted to a SpectrumCollection
    """
    return ex.classes_sp() + [ft.FileSpectrumList, ft.FileSparseCube, ft.FileFullCube]



# # Tries to "collaborate" with other packages
# "collaborator" packages: {"name": package}
__collaborators = OrderedDict()  # (("hypydrive",  a99),))

__PACKAGE_NAMES = ["f311.filetypes", "f311.explorer"]


def __setup_collaboration():
    """Will be executed in the first time someone calls classes_*() """
    global __collaborators, __flag_first
    __flag_first = False
    for pkgname in __PACKAGE_NAMES:
        try:
            pkg = importlib.import_module(pkgname)
            a99.get_python_logger().info("imported collaborator package '{}'".format(pkgname))

            try:
                if hasattr(pkg, "_setup_explorer"):
                    pkg._setup_explorer()
                else:
                    _collect_classes(pkg)

                __collaborators[pkgname] = pkg
            except:
                a99.get_python_logger().exception(
                    "hypydrive: actually, package '{}' gave error".format(pkgname))
                raise
        except:
            a99.get_python_logger().warning("failed to import package '{}".format(pkgname))
            pass


if __name__ == "__main__":
    import a99
    print(a99.classes_sp())