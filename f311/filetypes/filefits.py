__all__ = ["FileFits", "test_fits_magic"]

from .datafile import DataFile
from astropy.io import fits
from a99 import overwrite_fits


class FileFits(DataFile):
    """
    Generic representation of a FITS file

    **Note** normally, the DataFile classes load operation reads all contents
    and closes the file, however this class keeps the file **open** as an
    astropy.io.fits.HDUList object in self.hdulist, because apparently many
    HDUList methods need the file open to work, even after calling
    HDUList.readall()
    """

    # Take this out of explorer.py, too generic
    flag_collect = False
    flag_txt = False
    attrs = ["hdulist"]

    def __init__(self):
        DataFile.__init__(self)
        self.hdulist = None

    def _do_load(self, filename):
        self.hdulist = fits.open(filename)
        self.filename = filename

    def _do_save_as(self, filename):
        """Saves HDU list to FITS file."""
        overwrite_fits(self.hdulist, filename)


    def _test_magic(self, filename):
        test_fits_magic(filename)


def test_fits_magic(filename):
    """For FITS files, we assume that they must start with "SIMPLE".

    This may not be specified in the standard, but I have seen this in all the files I opened"""

    with open(filename, "rb") as file:
        chunk = file.read(4096 * 4)

        if not b"SIMPLE" in chunk:
            raise RuntimeError("File '{}' does not appear to be a FITS file".format(filename))
