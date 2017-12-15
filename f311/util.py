"""
Miscellanea routines that depend on other modules and sub-packages.
"""

import logging
import a99
from astropy.io import fits
from collections import OrderedDict
import textwrap


# TODO usage example for list_data_types(), or even a script

__all__ = [
    "load_any_file", "load_spectrum", "load_spectrum_fits_messed_x",
    "load_with_classes", "load", "get_filetypes_info",
    "filetypes_info_to_rows_header", "tabulate_filetypes_rest"]


def load(filename, class_):
    """Attempts to load file using a specific DataFile descendant.

    Arguments:
      filename -- full path to file
      class_ -- a DataFile descendant, or at least a class having method load() (duck typing)

    Returns: DataFile object if loaded successfully, or None if not.
    """
    return load_with_classes(filename, [class_])


def load_with_classes(filename, classes):
    """Attempts to load file by trial-and-error using a given list of classes.

    Arguments:
      filename -- full path to file
      classes -- list of classes having a load() method

    Returns: DataFile object if loaded successfully, or None if not.

    Note: it will stop at the first successful load.

    Attention: this is not good if there is a bug in any of the file readers,
    because *all exceptions will be silenced!*
    """

    ok = False
    for class_ in classes:
        obj = class_()
        try:
            obj.load(filename)
            ok = True
        # # cannot let IOError through because pyfits raises IOError!!
        # except IOError:
        #     raise
        # # also cannot let OSError through because astropy.io.fits raises OSError!!
        # except OSError:
        #     raise
        except FileNotFoundError:
            raise
        except Exception as e:  # (ValueError, NotImplementedError):
            # Note: for debugging, switch the below to True
            if a99.logging_level == logging.DEBUG:
                a99.get_python_logger().exception("Error trying with class \"{0!s}\"".format(
                                              class_.__name__))
            pass
        if ok:
            break
    if ok:
        return obj
    return None


def load_any_file(filename):
    """
    Attempts to load filename by trial-and-error

    Returns:
        file: A DataFile descendant, whose specific class depends on the file format detected, or None
        if the file canonot be loaded
    """
    import f311

    # Splits attempts using ((binary X text) file) criterion
    if a99.is_text_file(filename):
        return load_with_classes(filename, f311.classes_txt())
    else:
        return load_with_classes(filename, f311.classes_bin())

# def load_any_file_ex(filename):
#     """
#     Attempts to load filename by trial-and-error using _classes as list of classes.
#
#     Returns:
#         file, log_dict: A DataFile descendant, whose specific class depends on the file format detected, or None
#               if the file canonot be loaded
#     """
#     import f311
#
#     # Splits attempts using ((binary X text) file) criterion
#     if a99.is_text_file(filename):
#         return load_with_classes(filename, f311.classes_txt())
#     else:
#         return load_with_classes(filename, f311.classes_bin())


def load_spectrum(filename):
    """
    Attempts to load spectrum as one of the supported types.

    Returns:
        a Spectrum, or None
    """
    import f311

    f = load_with_classes(filename, f311.classes_sp())
    if f:
        return f.spectrum
    return None


def load_spectrum_fits_messed_x(filename, sp_ref=None):
    """Loads FITS file spectrum that does not have the proper headers. Returns a Spectrum"""
    import f311.filetypes as ft

    # First tries to load as usual
    f = load_with_classes(filename, (ft.FileSpectrumFits,))

    if f is not None:
        ret = f.spectrum
    else:
        hdul = fits.open(filename)

        hdu = hdul[0]
        if not hdu.header.get("CDELT1"):
            hdu.header["CDELT1"] = 1 if sp_ref is None else sp_ref.delta_lambda
        if not hdu.header.get("CRVAL1"):
            hdu.header["CRVAL1"] = 0 if sp_ref is None else sp_ref.x[0]

        ret = ft.Spectrum()
        ret.from_hdu(hdu)
        ret.filename = filename
        original_shape = ret.y.shape  # Shape of data before squeeze
        # Squeezes to make data of shape e.g. (1, 1, 122) into (122,)
        ret.y = ret.y.squeeze()

        if len(ret.y.shape) > 1:
            raise RuntimeError(
                "Data contains more than 1 dimension (shape is {0!s}), "
                "FITS file is not single spectrum".format(original_shape))

    return ret



FILE_TYPE_INFO_ATTRS = OrderedDict(zip(["description", "default_filename", "classname", "editors"],
                                       ["Description", "Default filename", "Class name", "Editors"]))


def get_filetypes_info(editor_quote="`", flag_leaf=True):
    """
    Reports available data types

    Args:
        editor_quote: character to enclose the name of the editor script between.
        flag_leaf: see tabulate_filetypes_rest()

    Returns:
        list: list of FileTypeInfo
    """
    NONE_REPL = ""
    import f311
    data = []  # [FileTypeInfo, ...]

    for attr in f311.classes_file(flag_leaf):
        description = a99.get_obj_doc0(attr)

        def_ = NONE_REPL if attr.default_filename is None else attr.default_filename
        ee = attr.editors
        if ee is None:
            ee = NONE_REPL
        else:
            # Example: "``mained.py``, ``x.py``"
            ee = ", ".join(["{0}{1}{0}".format(editor_quote, x, editor_quote) for x in ee])

        data.append({"description": description, "default_filename": def_, "classname": attr.__name__,
                     "editors": ee, "class": attr, "txtbin": "text" if attr.flag_txt else "binary"})

    data.sort(key=lambda x: x["description"])

    return data


def filetypes_info_to_rows_header(infos, attrnames=None, header=None, flag_wrap_description=False,
                                  description_width=40):
    """
    Converts filetype information to a (multiline_rows, header) tuple that can be more easily be tabulated

    **Attention** uses ReST syntax, using a "|br|" marker for line break. It requires the .rst source
                  file to contain the following bit:

        .. |br| raw:: html

           <br />

    Args:
        infos: list of FileTypeInfo
        attrnames: list of attribute names (keys of FILE_TYPE_INFO_ATTRS).
                   Defaults to all attributes
        header: list of strings containing headers. If not passed, uses default names
        flag_wrap_description: whether to wrap the description text
        description_width: width to wrap the description text (effective only if
                           flag_wrap_description is True)

    Returns:
        tuple: (rows, header): rows is a list of lists
    """

    if attrnames is None:
        attrnames = FILE_TYPE_INFO_ATTRS.keys()
    if header is None:
        header = [FILE_TYPE_INFO_ATTRS[key] for key in attrnames]

    if flag_wrap_description:
        wr = textwrap.TextWrapper(width=description_width, subsequent_indent="|br| ")

    data = []
    for i, info in enumerate(infos):
        row = []
        for j, attrname in enumerate(attrnames):
            if attrname != "description" or not flag_wrap_description:
                row.append(info[attrname])
            else:
                row.append(wr.wrap(info[attrname]))
        data.append(row)

    return data, header



#
#     return tabulate.tabulate(data, header)
# a99.markdown_table(("File type description", "Default filen


def tabulate_filetypes_rest(attrnames=None, header=None, flag_wrap_description=True,
                            description_width=40, flag_leaf=True):
    """
    Generates a reST multirow table

    Args:
        attrnames: list of attribute names (keys of FILE_TYPE_INFO_ATTRS).
                   Defaults to all attributes
        header: list of strings containing headers. If not passed, uses default names
        flag_wrap_description: whether to wrap the description text
        description_width: width to wrap the description text (effective only if
                           flag_wrap_description is True)
        flag_leaf: returns only classes that do not have subclasses
                   ("leaf" nodes as in a class tree graph)
    """

    infos = get_filetypes_info(editor_quote="``", flag_leaf=flag_leaf)
    rows, header = filetypes_info_to_rows_header(infos, attrnames, header, flag_wrap_description,
                                                 description_width)
    ret = a99.rest_table(rows, header)
    return ret
