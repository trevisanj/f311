"""
Miscellanea routines that depend on other modules and sub-packages.
"""

import logging
import a99
from .. import filetypes as ft
from astropy.io import fits

# TODO usage example for list_data_types(), or even a script

__all__ = [
    "load_any_file", "load_spectrum", "load_spectrum_fits_messed_x", "list_data_types",
]

def load_any_file(filename):
    """
    Attempts to load filename by trial-and-error using _classes as list of classes.
    """

    # Splits attempts using ((binary X text) file) criterion
    if a99.is_text_file(filename):
        return a99.load_with_classes(filename, ft.classes_txt())
    else:
        return a99.load_with_classes(filename, ft.classes_bin())


def load_spectrum(filename):
    """
    Attempts to load spectrum as one of the supported types. Returns a Spectrum, or None
    """
    f = a99.load_with_classes(filename, ft.classes_sp())
    if f:
        return f.spectrum
    return None


def load_spectrum_fits_messed_x(filename, sp_ref=None):
    """Loads FITS file spectrum that does not have the proper headers. Returns a Spectrum"""

    # First tries to load as usual
    f = a99.load_with_classes(filename, (ft.FileSpectrumFits,))

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
    ll = []  # [(description, default filename), ...]

    for attr in ft.classes_file():
        doc = attr.__doc__
        doc = attr.__name__ if doc is None else doc.strip().split("\n")[0]

        def_ = attr.default_filename
        def_ = def_ if def_ is not None else "-"
        ll.append((doc, def_))

    ll.sort(key=lambda x: x[0])

    return a99.markdown_table(("File type", "Default filename (for all purposes)"), ll)
