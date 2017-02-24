"""
Miscellanea routines that depend on other modules and sub-packages.
"""

import logging
import a99
# from f311 import filetypes as ft
from astropy.io import fits

# TODO usage example for list_data_types(), or even a script

__all__ = [
    "load_any_file", "load_spectrum", "load_spectrum_fits_messed_x", "list_data_types",
    "load_with_classes", "load"]


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
    Attempts to load filename by trial-and-error using _classes as list of classes.

    Returns:
        A DataFile descendant, whose specific class depends on the file format detected, or None
        if the file canonot be loaded
    """
    from f311 import filetypes as ft

    # Splits attempts using ((binary X text) file) criterion
    if a99.is_text_file(filename):
        return load_with_classes(filename, ft.classes_txt())
    else:
        return load_with_classes(filename, ft.classes_bin())


def load_spectrum(filename):
    """
    Attempts to load spectrum as one of the supported types.

    Returns:
        a Spectrum, or None
    """
    from f311 import filetypes as ft

    f = load_with_classes(filename, ft.classes_sp())
    if f:
        return f.spectrum
    return None


def load_spectrum_fits_messed_x(filename, sp_ref=None):
    """Loads FITS file spectrum that does not have the proper headers. Returns a Spectrum"""
    from f311 import filetypes as ft

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


def list_data_types():
    """
    Returns a list with all data types, in Markdown table format
    """
    from f311 import filetypes as ft
    ll = []  # [(description, default filename), ...]

    for attr in ft.classes_file():
        doc = attr.__doc__
        doc = attr.__name__ if doc is None else doc.strip().split("\n")[0]

        def_ = attr.default_filename
        def_ = def_ if def_ is not None else "-"
        ll.append((doc, def_))

    ll.sort(key=lambda x: x[0])

    return a99.markdown_table(("File type", "Default filename (for all purposes)"), ll)
