"""Classes FileSpectrum and descendants"""

__all__ = ["FileSpectrum", "FileSpectrumXY", "FileSpectrumFits"]


from .spectrum import Spectrum
import logging
from .datafile import DataFile
from a99 import overwrite_fits, write_lf
import a99
from astropy.io import fits
import os
import numpy as np
from .filefits import test_fits_magic

class FileSpectrum(DataFile):
    """Base class for all files representing a single 1D spectrum"""
    attrs = ['spectrum']
    editors = ["splisted.py"]

    def __init__(self):
        DataFile.__init__(self)
        self.spectrum = Spectrum()

    def load(self, filename=None):
        """Method was overriden to set spectrum.filename as well"""
        DataFile.load(self, filename)
        self.spectrum.filename = filename


class FileSpectrumXY(FileSpectrum):
    """
    "Lambda-flux" Spectrum (2-column text file)

    File may have comment lines; these will be ignored altogether, because the file
    is read with numpy.loadtxt()
    """

    def _do_load(self, filename):
        A = np.loadtxt(filename)
        if len(A.shape) < 2:
            raise RuntimeError("File {0!s} does not contain 2D array".format(filename))
        if A.shape[1] < 2:
            raise RuntimeError("File {0!s} must contain at least two columns".format(filename))
        if A.shape[1] > 2:
            a99.get_python_logger().warning("File {0!s} has more than two columns, taking only first and second".format(filename))
        sp = self.spectrum = Spectrum()
        sp.x = A[:, 0]
        sp.y = A[:, 1]


    def _do_save_as(self, filename):
        with open(filename, "w") as h:
            for x, y in zip(self.spectrum.x, self.spectrum.y):
                write_lf(h, "{0:.10g} {1:.10g}".format(x, y))


class FileSpectrumFits(FileSpectrum):
    """FITS Spectrum"""
    flag_txt = False

    def _do_load(self, filename):
        fits_obj = fits.open(filename)

        if len(fits_obj) > 1:
            raise RuntimeError("File has more than 1 frame, probably not a FITS spectrum")

        # fits_obj.info()
        hdu = fits_obj[0]
        hdu.verify()
        sp = self.spectrum = Spectrum()
        sp.from_hdu(hdu)

    def _do_save_as(self, filename):
        """Saves spectrum back to FITS file."""

        if len(self.spectrum.x) < 2:
            raise RuntimeError("Spectrum must have at least two points")
        if os.path.isfile(filename):
            os.unlink(filename)  # PyFITS does not overwrite file

        hdu = self.spectrum.to_hdu()
        overwrite_fits(hdu, filename)

    def _test_magic(self, filename):
        test_fits_magic(filename)

