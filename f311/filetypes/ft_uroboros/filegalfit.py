import a99
from .. import DataFile
from astropy.io import fits

__all__ = ["FileGalfit"]

@a99.froze_it
class FileGalfit(DataFile):
    """FITS file with 20 frames which is the output of Galfit software"""
    attrs = []
    description = "Galfit output"
    default_filename = None
    flag_txt = False

    def __init__(self):
        DataFile.__init__(self)
        self.hdulist = None

    def _do_load(self, filename):
        f = fits.open(filename)
        if len(f) != 20:
            raise RuntimeError("Not a {} file".format(self.__class__.__name__))
        self.hdulist = f

    def _do_save_as(self, filename):
        a99.overwrite_fits(self.hdulist, filename)
