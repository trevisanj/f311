"""
Collaboration-related routines

1) Class Catalog -- resources to retrieve File* classes by different criteria

2) Script utilities: collect scripts (standalone applications) across collaborator packages
"""


from collections import OrderedDict
import importlib
import a99
import os
import glob
import copy


__all__ = [
    "COLLABORATORS_C", "COLLABORATORS_S",
    "classes_txt", "classes_bin", "classes_sp", "classes_file",
    "get_suitable_vis_classes", "get_suitable_vis_list_classes",
    "get_scripts_path", "get_programs_dict",
    "EXTERNAL_COLLABORATORS"
    ]

# List of Python packages to be considered "external collaborators"
#
# These packages may contribute with:
# - scripts
# - DataFile subclasses
# - Vis subclasses
EXTERNAL_COLLABORATORS = ["pyfant", "aosss", "convmolworks", "ariastro"]


# List of **classes** collaborators packages (**change to add**)
#
COLLABORATORS_C = ["f311"]+EXTERNAL_COLLABORATORS
# List of **script** collaborator packages to look for scripts (**change to add**)
#
__F311 = ["f311"]+["f311."+x for x in a99.get_subpackages_names(os.path.split(__file__)[0])]
COLLABORATORS_S = __F311+EXTERNAL_COLLABORATORS


# **        ****                ******        ****                ******        ****
#   **    **    ******    ******      **    **    ******    ******      **    **    ******    ******
#     ****            ****              ****            ****              ****            ****
#
# Class catalog-related routines


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


def classes_file(flag_leaf=False):
    """All known File* classes

    Args:
        flag_leaf: returns only classes that do not have subclasses
                   ("leaf" nodes as in a class tree graph)
    """
    if __flag_first:
        __setup()

    if not flag_leaf:
        return _classes_file

    return [cls for cls in _classes_file if cls not in _classes_file_superclass]


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

    global _classes_file_superclass
    _classes_file_superclass = [cls.__bases__[0] for cls in _classes_file]


# # List of classes representing all file formats either read or written
#   ====================================================================
_classes_txt = []
_classes_bin = []
_classes_sp = []
_classes_file = []
_classes_file_superclass = []  # superclasses of items in _classes_file
_classes_vis = []
__flag_first = True
__collaborators = OrderedDict()


def __setup():
    """Will be executed in the first time someone calls classes_*() """
    global __collaborators, __flag_first

    import f311

    __flag_first = False
    for pkgname in f311.COLLABORATORS_C:
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
            # raise


# **        ****                ******        ****                ******        ****
#   **    **    ******    ******      **    **    ******    ******      **    **    ******    ******
#     ****            ****              ****            ****              ****            ****
#
# Scripts-related routines

def get_scripts_path(packagename):
    """**Convention** Returns full path to scripts directory"""
    return os.path.join(packagename, "scripts")


# {"packagename0": {"exeinfo": [ExeInfo00, ...], "description": description0}, ...}
# keys in COLLABORATORS_S
__programs_dict = None


def _get_programs_dict():
    """
    Builds and returns programs dictionary

    This will have to import the packages in COLLABORATORS_S in order to get their absolute path.

    Returns:
        dictionary: {"packagename": [ExeInfo0, ...], ...}

    "packagename" examples: "f311.explorer", "numpy"
    """
    global __programs_dict

    if __programs_dict is not None:
        return __programs_dict

    d = __programs_dict = OrderedDict()

    for pkgname in COLLABORATORS_S:
        try:
            package = importlib.import_module(pkgname)
        except ImportError:
            # I think it is better to be silent when a collaborator package is not installed
            continue

        path_ = os.path.join(os.path.split(package.__file__)[0], "scripts")
        bulk = a99.get_exe_info(path_, flag_protected=True)
        d[pkgname] = {"description": a99.get_obj_doc0(package), "exeinfo": bulk}

    return __programs_dict


def get_programs_dict(pkgname_only=None, flag_protected=False):
    """
    Scans COLLABORATORS_S packages for scripts, eventually filtering if arguments passed

    Args:
        pkgname_only: name of single package within COLLABORATORS_S
        flag_protected: include scripts starting with "_"?

    Returns:
        dictionary: {"packagename0": {"exeinfo": [ExeInfo00, ...], "description": description0}, ...}
    """

    ___ret = _get_programs_dict()
    __ret = ___ret if pkgname_only is None else OrderedDict(((pkgname_only, ___ret[pkgname_only]),))
    if flag_protected:
        _ret = __ret
    else:
        _ret = copy.deepcopy(__ret)
        for value in _ret.values():
            value["exeinfo"] = [exeinfo for exeinfo in value["exeinfo"] if not exeinfo.filename.startswith("_")]

    # Removes packages that may have gone out of scripts after filtering
    ret = _ret if pkgname_only is None and flag_protected is None else \
        OrderedDict(((key, value) for key, value in _ret.items() if len(value["exeinfo"]) > 0))

    return ret
