"""
"Collaboration" with other packages
"""


from collections import OrderedDict
import importlib
import a99

__all__ = ["classes_vis", "get_suitable_vis_classes"]


__COLLABORATORS = ["f311.explorer"]


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
#     Example: {"f311.explorer": f311.explorer, }
#     """
#     if __flag_first:
#         __setup()
#     return __collaborators

def _collect_classes(m):
    """
    Adds entries to _classes_*

    Args:
        m: module object that must contain the following sub-modules: datatypes, vis
    """

    from f311 import explorer as ex

    def _extend(classes, newclasses):
        """Filters out classes already present in list.

        This shouldn't be necessary, but collaborators may accidentally import already loaded
        classes into the datatypes namespace"""
        classes.extend([class_ for class_ in newclasses if class_ not in classes])

    # All kwnown Vis* classes
    _extend(_classes_vis, a99.get_classes_in_module(m, ex.Vis))


def classes_vis():
    """All known Vis* classes"""
    if __flag_first:
        __setup()
    return _classes_vis


_classes_vis = []
__flag_first = True
__collaborators = OrderedDict()  # (("pkg",  pkg),))


def __setup():
    """Will be executed in the first time someone calls classes_*() """
    global __collaborators, __flag_first
    __flag_first = False
    for pkgname in __COLLABORATORS:
        try:
            pkg = importlib.import_module(pkgname)
            a99.get_python_logger().info("Imported collaborator package '{}'".format(pkgname))

            try:
                if hasattr(pkg, "_setup_explorer"):
                    pkg._setup_explorer()
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
