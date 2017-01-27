"""
Miscellanea routines that depend on other modules and sub-packages.

Rule: only 'gui/' modules can import util!!!
"""

import numpy as np
import copy
import shutil
from astropy.io import fits
import logging
import a99
from f311.filetypes import *
from .. import explorer as ex
from .. import physics as ph

__all__ = [
    "load_any_file", "load_spectrum", "load_spectrum_fits_messed_x", "list_data_types",
    "cut_spectrum", "load_with_classes", "crop_splist"
]


###############################################################################
# # Routines to load file of unknown format


def load_with_classes(filename, classes):
    """Attempts to load file by trial-and-error using a given list of classes.

    Arguments:
      filename -- full path to file
      classes -- list of DataFile descendant classes

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
    """

    # Splits attempts using ((binary X text) file) criterion
    if a99.is_text_file(filename):
        return ex.load_with_classes(filename, ex.classes_txt())
    else:
        return ex.load_with_classes(filename, ex.classes_bin())


def load_spectrum(filename):
    """
    Attempts to load spectrum as one of the supported types. Returns a Spectrum, or None
    """
    f = ex.load_with_classes(filename, ex.classes_sp())
    if f:
        return f.spectrum
    return None


def load_spectrum_fits_messed_x(filename, sp_ref=None):
    """Loads FITS file spectrum that does not have the proper headers. Returns a Spectrum"""

    # First tries to load as usual
    f = ex.load_with_classes(filename, (FileSpectrumFits,))

    if f is not None:
        ret = f.spectrum
    else:
        hdul = fits.open(filename)

        hdu = hdul[0]
        if not hdu.header.get("CDELT1"):
            hdu.header["CDELT1"] = 1 if sp_ref is None else sp_ref.delta_lambda
        if not hdu.header.get("CRVAL1"):
            hdu.header["CRVAL1"] = 0 if sp_ref is None else sp_ref.x[0]

        ret = Spectrum()
        ret.from_hdu(hdu)
        ret.filename = filename
        original_shape = ret.y.shape  # Shape of data before squeeze
        # Squeezes to make data of shape e.g. (1, 1, 122) into (122,)
        ret.y = ret.y.squeeze()

        if len(ret.y.shape) > 1:
            raise RuntimeError(
                "Data contains more than 1 dimension (shape is {0!s}), FITS file is not single spectrum".format(
                original_shape))

    return ret


def list_data_types():
    """
    Returns a list with all data types, in Markdown table format
    """
    ll = []  # [(description, default filename), ...]


    for attr in ex.classes_file():
        doc = attr.__doc__
        doc = attr.__name__ if doc is None else doc.strip().split("\n")[0]

        def_ = attr.default_filename
        def_ = def_ if def_ is not None else "-"
        ll.append((doc, def_))

    ll.sort(key=lambda x: x[0])

    return a99.markdown_table(("File type", "Default filename (for all purposes)"), ll)


def cut_spectrum(sp, l0, lf):
    """
    Cuts spectrum given a wavelength interval

    Arguments:
        sp -- Spectrum instance
        l0 -- initial wavelength
        lf -- final wavelength
    """

    if l0 >= lf:
        raise ValueError("l0 must be lower than lf")
    idx0 = np.argmin(np.abs(sp.x - l0))
    idx1 = np.argmin(np.abs(sp.x - lf))
    out = copy.deepcopy(sp)
    out.x = out.x[idx0:idx1]
    out.y = out.y[idx0:idx1]
    return out


def copy_default_data_file(filename, module=a99):
    """Copies file from ftpyfant/data/default directory to local directory."""
    fullpath = ex.get_default_data_path(filename, module=module)
    shutil.copy(fullpath, ".")


def get_rgb(self, visible_range=None, method=0):
    """Takes weighted average of rainbow colors RGB's

    Arguments:
        visible_range=None -- if passed, affine-transforms the rainbow colors
        method --
          0: rainbow colors
          1: RGB
    """

    if len(visible_range) < 2:
        raise RuntimeError("Invalid visible range: {0!s}".format(visible_range))
    if visible_range[1] <= visible_range[0]:
        raise RuntimeError(
            "Second element of visible range ({0!s}) must be greater than first element".format(
                visible_range))

    if method == 1:
        # new color system splitting visible range in three
        dl = float(visible_range[1] - visible_range[0]) / 3
        ranges = np.array(
            [[visible_range[0] + i * dl, visible_range[0] + (i + 1) * dl] for i in range(3)])
        colors = np.array([(0., 0., 1.), (0., 1., 0.), (1., 0., 0.)])  # blue, green, red

        tot_area, tot_sum = 0., np.zeros(3)
        for color, range_ in zip(colors, ranges):
            b = np.logical_and(self.x >= range_[0], self.x <= range_[1])
            area = np.sum(self.y[b])
            tot_area += area
            tot_sum += color * area
        if tot_area == 0.:
            tot_area = 1.
        ret = tot_sum / tot_area
        return ret

    elif method == 0:
        tot_area, tot_sum = 0., np.zeros(3)

        def ftrans(x):
            return x

        if visible_range:
            ll0 = ph.rainbow_colors[0].l0
            llf = ph.rainbow_colors[-1].lf
            ftrans = lambda lold: visible_range[0] + (visible_range[1] - visible_range[0]) / (
            llf - ll0) * (lold - ll0)

        for color in ph.rainbow_colors:
            b = np.logical_and(self.x >= ftrans(color.l0), self.x <= ftrans(color.lf))
            area = np.sum(self.y[b])
            tot_area += area
            tot_sum += color.rgb * area
        if tot_area == 0.:
            tot_area = 1.
        ret = tot_sum / tot_area
        return ret
    else:
        raise RuntimeError("Unknown method: {0!s}".format(method))


def crop_splist(splist, lambda0=None, lambda1=None):
    """
    Cuts all spectra in SpectrumList

    **Note** lambda1 **included** in interval (not pythonic).
    """
    if len(splist.spectra) == 0:
        raise RuntimeError("Need at least one spectrum added in order to crop")

    if lambda0 is None:
        lambda0 = splist.wavelength[0]
    if lambda1 is None:
        lambda1 = splist.wavelength[-1]
    if not (lambda0 <= lambda1):
        raise RuntimeError('lambda0 must be <= lambda1')

    if not any([lambda0 != splist.wavelength[0], lambda1 != splist.wavelength[-1]]):
        return

    for i in range(len(splist)):
        sp = cut_spectrum(splist.spectra[i], lambda0, lambda1)
        if i == 0:
            n = len(sp)
            if n < 2:
                raise RuntimeError(
                    "Cannot cut, spectrum will have %d point%s" % (n, "" if n == 1 else "s"))
        splist.spectra[i] = sp

    splist.__update()