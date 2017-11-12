__all__ = ["FileSparseCube"]


import a99
from .. import DataFile
from . import SparseCube
from astropy.io import fits


@a99.froze_it
class FileSparseCube(DataFile):
    """FITS Sparse Data Cube (storage to take less disk space)"""
    attrs = ['sparsecube']
    default_filename = "default.sparsecube"
    flag_txt = False

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
        a99.overwrite_fits(hdul, filename)

    def init_default(self):
        # Already created OK
        pass
