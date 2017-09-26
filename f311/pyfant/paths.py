import os
import glob
import platform
import a99


__all__ = [
    "get_pfant_path", "get_pfant_data_path", "get_pfant_data_subdirs", "get_pfant_star_subdirs",
    "get_fortrans",
    ]


def get_pfant_path(*args):
    """
    Returns absolute path to the "PFANT" directory.

    PFANT binaries must be in PATH,
    otherwise it will not work

    Arguments passed will be incorporated into path
    """

    path_to_exe = a99.which("pfant")
    if path_to_exe is None:
        raise RuntimeError("Cannot find 'pfant' executable")

    p, _ = os.path.split(path_to_exe)

    return os.path.abspath(os.path.join(p, "..", "..", *args))


def get_pfant_data_path(*args):
    """Returns absolute path to PFANT/data"""
    return get_pfant_path("data", *args)


def get_pfant_data_subdirs():
    """returns a list containing all subdirectories of PFANT/data (their names only, not full path)."""
    dd = glob.glob(os.path.join(get_pfant_data_path(), "*"))
    ret = []
    for d in dd:
        if os.path.isdir(d):
            ret.append(os.path.basename(d))
    return ret


def get_pfant_star_subdirs():
    """Returns only subdirectories of PFANT/data that contain file main.dat."""
    dd = glob.glob(os.path.join(get_pfant_data_path(), "*"))
    ret = []
    for d in dd:
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'main.dat')):
            ret.append(os.path.basename(d))
    return ret


def get_fortrans(max_len=None):
    """
    Generates listing of files in the Fortran bin directory

    Arguments
      max_len: (optional) if passed, will use it, otherwise will be the
                 maximum number of characters among all Fortran executable names.

    Returns: list of a99.ExeInfo
    """

    ret = []

    flag_bindir = True
    try:
        bindir = os.path.join(get_pfant_path(), "fortran", "bin")
    except:
        flag_bindir = False

    ihpn = ["innewmarcs", "hydro2", "pfant", "nulbad"]
    if max_len is None:
        max_len = max(len(x) for x in ihpn)

    if platform.system() == "Windows":
        def has_it(x):
            return os.path.isfile(os.path.join(bindir, x+".exe"))
    else:
        def has_it(x):
            return os.path.isfile(os.path.join(bindir, x))
    for name in ihpn:
        status = "not found"
        if flag_bindir and has_it(name):
            status = "found"

        ret.append(a99.ExeInfo(name, status, flag_gui=None))
        # piece = name + " " + ("." * (max_len-len(name)))
        # ret.append(("%-"+str(max_len)+"s %s") % (piece, status))
    return ret


