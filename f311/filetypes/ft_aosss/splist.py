""""
List of spectra sharing same wavenumber axis. Uses FITS format
"""


__all__ = ["SpectrumList"]


from . import SpectrumCollection, FullCube
# from a99 import froze_it, cut_spectrum
from .. import Spectrum
from astropy.io import fits
import numpy as np
import a99


@a99.froze_it
class SpectrumList(SpectrumCollection):
    attrs = SpectrumCollection.attrs+["wavelength"]

    @property
    def delta_lambda(self):
        return self.wavelength[1]-self.wavelength[0]

    @property
    def flag_wled(self):
        """Wavelength problem already resolved?"""
        return self.wavelength[0] > -1

    def __init__(self, hdulist=None):
        SpectrumCollection.__init__(self)
        self.__flag_update = True
        self.__flag_update_pending = False
        self.wavelength = np.array([-1., -1.])  # the wavelength axis (angstrom) (shared among all spectra in the cube)

        if hdulist is not None:
            self.from_hdulist(hdulist)

    ############################################################################
    # # Interface

    def to_csv(self, sep=","):
        """Generates tabulated text

        Returns list of strings
        """
        lines = []
        lines.append(sep.join(self.fieldnames+[str(x)  for x in self.wavelength])+"\n")
        for sp in self.spectra:
            lines.append(sep.join([repr(sp.more_headers.get(fieldname)) for fieldname in self.fieldnames]+
                                  [str(flux) for flux in sp.y])+"\n")
        return lines


    def matrix(self):
        """Returns a (spectrum)x(wavelength) matrix of flux values"""
        n = len(self)
        if n == 0:
            return np.array()
        return np.vstack([sp.y for sp in self.spectra])

    def from_hdulist(self, hdul):
        self.__flag_update = False
        try:
            SpectrumCollection.from_hdulist(self, hdul)
        finally:
            self.enable_update()

    def from_full_cube(self, full_cube):
        """
        Adds all cube "pixels" (i.e., spectra) that are not all zero

        Very similar to SparseCube.from_full_cube() (bit simpler)
        """

        assert isinstance(full_cube, FullCube)
        hdu = full_cube.hdu
        assert isinstance(hdu, fits.PrimaryHDU)
        data = hdu.data

        # TODO implement threshold, i.e., abs(...) <= epsilon
        xx, yy = np.where(sum(data, 0) != 0)
        for i, j in zip(xx, yy):
            sp = full_cube.get_spectrum(i, j)
            sp.pixel_x, sp.pixel_y = i, j
            # TODO have to fill in filename first sp.more_headers["ORIGIN"] = os.path.basename(self.filename)
            self.add_spectrum(sp)


    def add_spectrum(self, sp):
        """Adds spectrum. Updates internal wavelength vector to maximum possible

        If wavelength vectors do not match, it will resample the new spectrum,
        and may expand self.wavelength, but will not shift the x-position of existing
        points
        """
        assert isinstance(sp, Spectrum)
        if len(sp.x) < 2:
            raise RuntimeError("Spectrum must have at least two points")

        if not self.flag_wled:
            self.wavelength = np.copy(sp.wavelength)
        else:
            if not np.all(self.wavelength == sp.wavelength):
                # print("VAI TER QUE RESAMPLEAR ALGO")
                xcur0, xcur1 = self.wavelength[0], self.wavelength[-1]
                xsp0, xsp1 = sp.x[0], sp.x[-1]

                # quantizes new wavelength interval to current delta_lambda step
                dl = self.delta_lambda

                xnew0 = xcur0 if xcur0 <= xsp0 else xcur0-np.floor((xcur0-xsp0)*dl)/dl
                xnew1 = xcur1 if xcur1 >= xsp1 else xcur1+np.floor((xsp1-xcur1)*dl)/dl

                n = int(np.round((xnew1-xnew0)/dl))+1
                self.wavelength = np.arange(n)*dl+xnew0

                if not (xnew0 == xcur0 and xnew1 == xcur1):
                    # print("RESAMPLEANDO EXISTING")
                    for sp_existing in self.spectra:
                        sp_existing.resample(self.wavelength)

                if not(xnew0 == xsp0 and xnew1 == xsp1 and dl == sp.delta_lambda):
                    # print("RESAMPLING NEWCOMER")
                    sp.resample(self.wavelength)
                else:
                    # print("NO NEED TO RESAMPLE NEWCOMER")
                    pass

                # raise RuntimeError("Cannot add spectrum, wavelength vector does not match existing")

        SpectrumCollection.add_spectrum(self, sp)
        self.__update()

    def delete_spectra(self, indexes):
        SpectrumCollection.delete_spectra(self, indexes)
        self.__update()

    def enable_update(self):
        self.__flag_update = True
        if self.__flag_update_pending:
            self.__update()
            self.__flag_update_pending = False


    def __update(self):
        """
        Updates internal state

        This consists of verifying whether or not there are spectra.
        If not, resets the wavelength vector.
        """

        if not self.__flag_update:
            self.__flag_update_pending = True
            return

        if len(self.spectra) == 0:
            self.wavelength = np.array([-1., -1.])
