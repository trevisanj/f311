from astropy.io import fits
from astropy import units as u
from scipy import interp
import numpy as np
import a99
import os

__all__ = ["Spectrum", "fnu", "flambda"]


# AstroPy units defined for convenience
fnu = u.erg/u.cm**2/u.s/u.Hz
flambda = u.erg/u.cm**2/u.s/u.angstrom


@a99.froze_it
class Spectrum(object):
    """
    Spectrum with several *in-place* operations, conversion utilities etc.

    Routines that have the term *in place*: it means that the spectrum
    itself is changed and nothing is returned
    """

    @property
    def xunit(self):
        """Unit of the wavelength axis (some unit from astropy.units)"""
        return self.more_headers["X-UNIT"]

    @xunit.setter
    def xunit(self, value):
        if not isinstance(value, (u.UnitBase,)):  #(u.Unit, u.CompositeUnit, u.IrreducibleUnit)):
            raise TypeError("Spectrum x-unit must be an astropy unit, not '{}'".format(str(value)))
        self.more_headers["X-UNIT"] = value

    @property
    def yunit(self):
        """Unit of the wavelength axis (some unit from astropy.units)"""
        return self.more_headers["Y-UNIT"]

    @yunit.setter
    def yunit(self, value):
        if not isinstance(value, (u.UnitBase,)):  #, (u.Unit, u.CompositeUnit)):
            raise TypeError("Spectrum y-unit must be an astropy unit, not '{}'".format(str(value)))
        self.more_headers["Y-UNIT"] = value

    @property
    def title(self):
        """"Title" of the spectrum. Returns self._title or if None, other options"""
        ret = self._title
        if ret is None and self.filename is not None:
            ret = os.path.split(self.filename)[1]
        if ret is None:
            ret = self.more_headers.get("ORIGIN")
        return ret

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def wavelength(self):
        """Wavelength vector. Equivalent to `wavelenght`"""
        return self.x

    @wavelength.setter
    def wavelength(self, x):
        self.x = x

    @property
    def l0(self):
        """Lower bound of wavelength vector"""
        return self.x[0]

    @property
    def lf(self):
        """Upper bound of wavelength vector"""
        return self.x[-1]

    @property
    def llzero(self):
        """Lower bound of wavelength vector. Synonym with l0"""
        return self.x[0]

    @property
    def llfin(self):
        """Upper bound of wavelength vector. Synonym with lf"""
        return self.x[-1]

    @property
    def flux(self):
        """Flux vector. Equivalent to `y`"""
        return self.y

    @flux.setter
    def flux(self, y):
        self.y = y

    @property
    def delta_lambda(self):
        """Returns delta lambda or NaN if found not to be constant"""
        ret = self.x[1]-self.x[0]
        if abs(self.x[-1]-self.x[-2]-ret) > 1e-5:
            return float("nan")
        return ret

    @property
    def pixel_x(self):
        return self.more_headers.get("PIXEL-X")

    @pixel_x.setter
    def pixel_x(self, value):
        self.more_headers["PIXEL-X"] = value

    @property
    def pixel_y(self):
        return self.more_headers.get("PIXEL-Y")
        
    @pixel_y.setter
    def pixel_y(self, value):
        self.more_headers["PIXEL-Y"] = value

    @property
    def z_start(self):
        return self.more_headers.get("Z-START")

    @z_start.setter
    def z_start(self, value):
        self.more_headers["Z-START"] = value

    # TODO maybe this is obsolete
    @property
    def ylabel(self):
        """Y-label for plotting purposes"""
        return self.more_headers.get("YLABEL")

    @ylabel.setter
    def ylabel(self, value):
        self.more_headers["YLABEL"] = value

    #*****************
    def __init__(self, x=None, y=None):
        self._flag_created_by_block = False  # assertion
        self.more_headers = {}
        self.x = x
        self.y = y
        # Default units
        self.xunit = u.angstrom
        self.yunit = fnu
        self.filename = None
        self.title = None

    def __len__(self):
        """Corresponds to nulbad "ktot"."""
        return len(self.x) if self.x is not None else 0

    def one_liner_str(self):
        if self.x is not None and len(self.x) > 0:
            # s = ", ".join(["%g <= lambda <= %g" % (self.x[0], self.x[-1]),
            #                "delta_lambda = %g" % self.delta_lambda,
            #                "no. points: %d" % len(self.x)])

            info = ["{0:g} \u2264 \u03BB \u2264 {1:g}".format(self.x[0], self.x[-1])]
            try:
                dl = self.delta_lambda
                info.append("\u0394\u03BB = {0:g}".format(dl))
            except:
                pass

            info.append("{0:g} \u2264 flux \u2264 {1:g}".format(np.min(self.y), np.max(self.y)))
            info.append("length: {0:d}".format(len(self.x)))

            s = " | ".join(info)
        else:
            s = "(empty)"
        return s

    def __str__(self):
        return self.one_liner_str()
        # s = ", ".join(["ikeytot = ", str(self.ikeytot), "\n",
        #                "tit = ", str(self.tit), "\n",
        #                "tetaef = ", str(self.tetaef), "\n",
        #                "glog = ", str(self.glog), "\n",
        #                "asalog = ", str(self.asalog), "\n",
        #                "modeles_nhe = ", str(self.modeles_nhe), "\n",
        #                "amg = ", str(self.amg), "\n",
        #                "l0 = ", str(self.l0), "\n",
        #                "lf = ", str(self.lf), "\n",
        #                "pas = ", str(self.pas), "\n",
        #                "echx = ", str(self.echx), "\n",
        #                "echy = ", str(self.echy), "\n",
        #                "fwhm = ", str(self.fwhm), "\n",
        #                "============\n"
        #                "Size of Spectrum: ", str(len(self)), "\n"])
        # return s

    def clear_more_headers(self):
        """Clears .more_headers dictionary, except for X-UNIT and Y-UNIT"""

        keys = list(self.more_headers.keys())
        for key in keys:
            if key not in ("X-UNIT", "Y-UNIT"):
                del self.more_headers[key]





    # header parameters *not* to be put automatically in self.more_headers
    #                  saved separately  dealt with automatically by the FITS module
    #                  ----------------  ------------------------------------------------
    _IGNORE_HEADERS = ("CRVAL", "CDELT", "NAXIS", "PCOUNT", "BITPIX", "GCOUNT", "XTENSION",
                       "XUNIT", "BUNIT", "SIMPLE", "EXTEND", "X-UNIT", "Y-UNIT", "UNITS2", "UNITS1")
    def from_hdu(self, hdu):
        # x/wavelength and y/flux
        n = hdu.data.shape[0]
        lambda0 = hdu.header["CRVAL1"]
        try:
            delta_lambda = hdu.header["CDELT1"]
        except Exception as E:  # todo figure out the type of exception (KeyError?)
            delta_lambda = hdu.header['CD1_1']
            print("Alternative delta lambda in FITS header: CD1_1")
            print("Please narrow the Exception specification in the code")
            print(("Exception is: " + str(E) + " " + E.__class__.__name__))
            print(delta_lambda)
        self.x = np.linspace(lambda0, lambda0 + delta_lambda * (n - 1), n)
        self.y = hdu.data

        _xunit = hdu.header.get("X-UNIT")
        if _xunit:
            self.xunit = u.Unit(_xunit)
        else:
            _xunit = hdu.header.get("XUNIT")
            if _xunit == "nm":
                self.xunit = u.nm
            elif _xunit == "A":
                self.xunit = u.angstrom
            else:
                #  Fallback to angstrom
                self.xunit = u.angstrom

        _yunit = hdu.header.get("Y-UNIT")
        if _yunit:
            self.yunit = u.Unit(_yunit)
        else:
            _yunit = hdu.header.get("BUNIT")
            if _yunit == "erg/s/cm2/Hz":
                self.yunit = fnu
            elif _yunit == "erg/s/cm2/A":
                self.yunit = flambda
            else:
                # y-units as in file C001231_spintg.fits (a card "UNITS2" with blank value exists,
                # but its comment is "electrons (TOTAL)")
                try:
                    _yunit = hdu.header.comments["UNITS1"]
                except KeyError:
                    try:
                        _yunit = hdu.header.comments["UNITS2"]
                    except KeyError:
                        _yunit = None

                if str(_yunit).startswith("electrons (TOTAL)"):
                    self.yunit = u.electron
                else:
                    # Fallback to dimensionless unit
                    self.yunit = u.Unit("")

        # Additional header fields
        for name in hdu.header:
            if not name.startswith(self._IGNORE_HEADERS):
                # **Note** that it eliminates "#" comments from FITS header
                value = hdu.header[name]
                if isinstance(value, str):
                    value = value.split("#")[0].strip()
                self.more_headers[name] = value

    def to_hdu(self):
        """Converts to FITS HDU. delta_lambda must be a constant"""

        if np.isnan(self.delta_lambda):
            # TODO add "spec" parameter to allow other FITS encoding for spectra
            raise RuntimeError("Cannot encode HDU because delta_lambda is not constant")

        hdu = fits.PrimaryHDU()
        # hdu.header[
        #     "telescop"] = "PFANT synthetic spectrum"  # "suggested" by https://python4astronomers.github.io/astropy/fits.html
        hdu.header["CRVAL1"] = self.x[0]
        hdu.header["CDELT1"] = self.delta_lambda


        _xunit = str(self.xunit)
        _yunit = str(self.yunit)
        hdu.header["X-UNIT"] = _xunit
        hdu.header["Y-UNIT"] = _yunit

        # AOSSS expectations
        _xunit = "(not supported)"
        _yunit = "(not supported)"
        if self.xunit == u.angstrom:
            _xunit = "A"
        elif self.xunit == u.nm:
            _xunit = "nm"
        if self.yunit == fnu:
            _yunit = "erg/s/cm2/Hz"
        elif self.yunit == flambda:
            _yunit = "erg/s/cm2/A"
        hdu.header["XUNIT"] = _xunit
        hdu.header["BUNIT"] = _yunit

        for key, value in list(self.more_headers.items()):
            if key in ("X-UNIT", "Y-UNIT"):
                continue

            try:
                # handles commentary cards
                #
                # http://docs.astropy.org/en/stable/io/fits/usage/headers.html#comment-history-and-blank-keywords
                if key in ("COMMENT", "HISTORY", ""):
                    if isinstance(value, str):
                        # proceeds as usual
                        hdu.header[key] = value
                    else:
                        # value is probably an instance of fits.header._HeaderCommentaryCards
                        for _ in value:
                            hdu.header[key] = _
                else:
                    hdu.header[key] = value
            except:
                a99.get_python_logger().exception("Error adding header['{0!s}'] = '{1!s}'".format(key, value))
                raise
        hdu.data = self.y
        return hdu
        
    def cut(self, l0, l1):
        """Cuts *in place* to wavelength interval [l0, l1]. Cut is done within the array objects thus keeping the same objects"""
        ii_delete = np.where(np.logical_or(self.x < l0, self.x > l1))
        self.x = np.delete(self.x, ii_delete)
        self.y = np.delete(self.y, ii_delete)
        
    def cut_idxs(self, i0, i1):
        """Cuts *in place* to slice i0:i1 (pythonic, interval = [i0, i1["""
        self.x = self.x[i0:i1]
        self.y = self.y[i0:i1]

    def resample(self, new_wavelength, kind='linear'):
        """Resamples *in-place* to new wavelength vector using interpolation

        Args:
            new_wavelength: new wavelength vector
            kind: interpolation kind to be passed to scipy.interpolate.interp1d
        """
        # f = interp1d(self.x, self.y, kind='linear', bounds_error=True, fill_value=0)
        self.y = interp(new_wavelength, self.x, self.y)
        self.wavelength = new_wavelength


    def convert_x(self, new_unit):
        """Converts x-axis to new unit"""

    # def flambda_to_fnu(self):
    #     """
    #     Flux-nu to flux-lambda conversion **in-place**
    #
    #     Formula:
    #         f_nu = f_lambda*(lambda/nu) = f_lambda*lambda**2/c
    #
    #         where
    #             lambda is the wavelength in cm,
    #             c is the speed of light in cm/s
    #             f_lambda has irrelevant unit for this purpose
    #
    #     **Note** By convention in this library, Spectrum wavelength is always in angstrom
    #     """
    #
    #     x_cm = self.x*1e-8
    #     self.y *= 1./(1e-8 * C) * x_cm ** 2
    #
    # def fnu_to_flambda(self):
    #     """
    #
    #     **in-place** flux-lambda to flux-nu conversion
    #
    #     Converts flux from erg/s/cm**2/Hz
    #                     to erg/s/cm**2/angstrom
    #     Formula:
    #         f_lambda = f_nu*(nu/lambda) = f_nu*c/lambda**2
    #
    #         (terms description are the same as in flambda_to_fnu())
    #     """
    #
    #     x_cm = self.x * 1e-8  # angstrom -to cm
    #     #    y * C/x_cm ** 2  would be in erg/s/cm**2/cm
    #     # 1e-8 * C/x_cm ** 2        is in erg/s/cm**2/angstrom
    #     self.y *= 1e-8 * C/x_cm ** 2
