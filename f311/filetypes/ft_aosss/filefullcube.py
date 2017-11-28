__all__ = ["FileFullCube"]


from . import FullCube
from astropy.io import fits
import a99
# import f311.explorer as ex
from .. import DataFile


@a99.froze_it
class FileFullCube(DataFile):
    """
    FITS WebSim Compass Data Cube

    "full" opposed to "sparse"

    **Note** normally, the DataFile classes load operation reads all contents
    and closes the file, however this class keeps the file **open** as an
    astropy.io.fits.HDUList object in self.hdulist, because apparently many
    HDUList methods need the file open to work, even after calling
    HDUList.readall()
    """
    attrs = ['wcube']
    description = ""
    default_filename = "default.fullcube"
    flag_txt = False
    editors = ["cubeed.py"]

    def __init__(self):
        DataFile.__init__(self)
        self.wcube = FullCube()
        self.hdulist = None

    def _do_load(self, filename):
        o = fits.open(filename)

        if not "Puech" in o[0].header.comments["COMMENTS"]:
            raise RuntimeError("Word 'Puech' not find in header comments")

        self.hdulist = o

        self.wcube = FullCube(self.hdulist[0])
        self.filename = filename

    def _do_save_as(self, filename):
        if not self.wcube.flag_wavelengthed:
            raise RuntimeError("Cannot save before at least one pixel has been \"painted\"""")
        a99.overwrite_fits(self.wcube.hdu, filename)
