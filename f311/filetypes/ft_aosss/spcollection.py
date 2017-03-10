""""
List of spectra sharing same wavenumber axis. Uses FITS format
"""
# from a99 import Spectrum, AttrsPart, froze_it, eval_fieldnames
import a99
from astropy.io import fits
import os
import numpy as np
import numbers
import copy
# import f311.physics as ph
# import f311.filetypes as ft
from .. import Spectrum

__all__ = ["SpectrumCollection"]


class SpectrumCollection(a99.AttrsPart):
    """Base class, maintains spectra with "more headers"; to/from HDU without much interpretation"""

    attrs = ["fieldnames", "more_headers", "spectra"]

    def __init__(self):
        a99.AttrsPart.__init__(self)
        self._flag_created_by_block = False  # assertion
        self.filename = None
        # _LambdaReference instance, can be inferred from first spectrum added
        self.spectra = []
        # List of field names
        self.fieldnames = []
        # Visible field names (GUI setup purpose); order is same as column order in table widget
        self.fieldnames_visible = []
        self.more_headers = {}

    def __len__(self):
        return len(self.spectra)

    # def __getitem__(self, item):
    #     """Return copy of self with sliced self.spectra"""
    #     ret = copy.copy(self)
    #     ret.spectra = self.spectra.__getitem__(item)

    # - NAXIS(1/2/3) apparently managed by pyfits
    # - FIELDNAM & FIELDN_V are parsed separately
    _IGNORE_HEADERS = ("NAXIS", "FIELDNAM", "FIELDN_V")

    def from_hdulist(self, hdul):
        assert isinstance(hdul, fits.HDUList)
        if not (hdul[0].header.get("ANCHOVA") or hdul[0].header.get("TAINHA")):
            raise RuntimeError("Wrong HDUList")

        self.spectra = []
        for i, hdu in enumerate(hdul):
            if i == 0:
                # Additional header fields
                for name in hdu.header:
                    if not name.startswith(self._IGNORE_HEADERS):
                        self.more_headers[name] = hdu.header[name]

                # self.fieldnames is not overwritten if there is no such information in HDU
                temp = hdu.header.get("FIELDNAM")
                if temp:
                    self.fieldnames = a99.eval_fieldnames(temp)
                # self.fieldnames_visible is overwritten yes
                temp = hdu.header.get("FIELDN_V")
                if temp is None:
                    self.fieldnames_visible = copy.copy(self.fieldnames)
                else:
                    self.fieldnames_visible = a99.eval_fieldnames(temp)
            else:
                sp = Spectrum()
                sp.from_hdu(hdu)
                self.add_spectrum(sp)

    def to_hdulist(self):
        # I think this is not or should not be a restriction assert len(self.spectra) > 0, "No spectra added"

        # dl = self.delta_lambda

        hdul = fits.HDUList()

        hdu = fits.PrimaryHDU()
        hdu.header["FIELDNAM"] = str(self.fieldnames)
        hdu.header["FIELDN_V"] = str(self.fieldnames_visible)
        hdu.header["ANCHOVA"] = 26.9752

        hdu.header.update(self.more_headers)
        hdul.append(hdu)

        for sp in self.spectra:
            hdul.append(sp.to_hdu())

        return hdul

    def collect_fieldnames(self):
        """Returns a list of unique field names union'ing all spectra field names"""
        # self.fieldnames = []
        ff = []
        for sp in self.spectra:
            ff.extend(list(sp.more_headers.keys()))
        return list(set(ff))

    def add_spectrum(self, sp):
        """Adds spectrum, no content check

        Updates self.fieldnames to expose sp.more_headers

        Nullifies spectrum filename and assigns the file basename to more_headers["ORIGIN"]
        """
        assert isinstance(sp, Spectrum)

        if sp.filename is not None:
            sp.more_headers["ORIGIN"] = os.path.basename(sp.filename)
            sp.filename = None
        self.spectra.append(sp)

        for name in sp.more_headers:
            if name not in self.fieldnames:
                self.fieldnames.append(name)

    def delete_spectra(self, indexes):
        """Deletes spectra given a list of 0-based indexes"""
        if isinstance(indexes, numbers.Integral):
            indexes = [indexes]
        indexes = list(set(indexes))
        n = len(self.spectra)
        if any([idx < 0 or idx >= n for idx in indexes]):
            raise RuntimeError("All indexes must be (0 le index lt %d)" % n)
        for index in reversed(indexes):
            del self.spectra[index]

    def clear(self):
        """Removes all spectra from the collection"""
        self.spectra = []

    def merge_with(self, other, default_pixel_x=None, default_pixel_y=None):
        """Adds spectra from other SpectrumCollection to self"""
        assert isinstance(other, SpectrumCollection)
        for sp in other.spectra:
            self.add_spectrum(sp)


    # def to_colors(self, visible_range=None, flag_scale=False, method=0):
    #     """Returns a [n, 3] red-green-blue (0.-1.) matrix
    #
    #     Args:
    #       visible_range=None: if passed, the true human visible range will be
    #                             affine-transformed to visible_range in order
    #                             to use the red-to-blue scale to paint the pixels
    #       flag_scale: whether to scale the luminosities proportionally
    #                     the weight for each spectra will be the area under the flux
    #       method: see Spectrum.get_rgb()
    #     """
    #     weights = np.zeros((len(self), 3))
    #     max_area = 0.
    #     ret = np.zeros((len(self), 3))
    #     for i, sp in enumerate(self.spectra):
    #         ret[i, :] = ph.spectrum_to_rgb(sp, visible_range, method)
    #         sp_area = np.sum(sp.y)
    #         max_area = max(max_area, sp_area)
    #         weights[i, :] = sp_area
    #     if flag_scale:
    #         weights *= 1. / max_area
    #         ret *= weights
    #     # TODO return weights if necessary
    #     return ret
