__all__ = ["FileSparseCube"]


from a99 import DataFile, froze_it, overwrite_fits
from . import SparseCube
from astropy.io import fits


@froze_it
class FileSparseCube(DataFile):
    """FITS Sparse Data Cube (storage to take less disk space)"""
    attrs = ['sparsecube']
    description = "Data Cube (FITS file)"
    default_filename = "default.sparsecube"

    def __init__(self):
        DataFile.__init__(self)
        self.sparsecube = SparseCube()

    def _do_load(self, filename):
        fits_obj = fits.open(filename)
        self.sparsecube = SparseCube()
        self.sparsecube.from_hdulist(fits_obj)
        self.filename = filename

    def _do_save_as(self, filename):
        hdul = self.sparsecube.to_hdulist()
        overwrite_fits(hdul, filename)

    def init_default(self):
        # Already created OK
        pass
