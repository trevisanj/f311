__all__ = ["MAGNITUDE_BASE", "STDFLUX", "calculate_magnitude", "get_vega_spectrum",
           "Bandpass", "UBVTabulated", "UBVParametric", "get_ubv_bandpasses",
           "get_zero_flux", "flux_to_mag", "mag_to_flux", "get_ubv_bandpass",
           "get_ubv_bandpasses_dict", "calc_mag"]


import numpy as np
import collections
from scipy.interpolate import interp1d
import copy
import a99
import f311.filetypes as ft
# from .. import physics as ph

MAGNITUDE_BASE = 100. ** (1. / 5)  # approx. 2.512
_REF_NUM_POINTS = 5000   # number of evaluation points over entire band range


_ubv_bandpasses = None
_ubv_bandpasses_dict = None
def get_ubv_bandpasses():
    """Returns list with UBVRI... Bandpass objects"""
    global _ubv_bandpasses, _ubv_bandpasses_dict
    if _ubv_bandpasses is None:
        _ubv_bandpasses = []
        _ubv_bandpasses_dict = collections.OrderedDict()
        for name in UBVParametric.X0_FWHM.keys():
            bp = UBVTabulated(name) if name in "UBVRI" else UBVParametric(name)
            _ubv_bandpasses.append(bp)
            _ubv_bandpasses_dict[name] = bp
    return _ubv_bandpasses


def get_ubv_bandpasses_dict():
    """Returns dictionary with band name, i.e., U/B/V/etc. as dict"""
    get_ubv_bandpasses()  # just to assure the dict is assembled
    return _ubv_bandpasses_dict


def get_ubv_bandpass(bp):
    """Returns a BandPass object for given band name

    Args:
        bp: band name or BandPass object

    Returns:
        f311.physics.BandPass: BandPass object. If `bp` is already a BandPass object, returns `bp`
    """
    if isinstance(bp, Bandpass):
        return bp
    get_ubv_bandpasses()  # just to assure the dict is assembled
    return _ubv_bandpasses_dict[bp]


def calc_mag(sp, bp, system="stdflux", zero_point=0., flag_force_band_range=False):
    """
    Calculates magnitude from a Spectrum object. See calculate_magnitude for arguments documentation

    Returns: (float) calculated magnitude

    Example:

    >>> # The following example prints a table showing the calculated magnitude for the
    >>> # Vega spectrum in several systems
    >>> import f311.physics as ph
    >>> import tabulate
    >>> systems = ["stdflux", "ab", "vega"]
    >>> bands = "UBVRIJHK"
    >>> sp = ph.get_vega_spectrum()
    >>> rows = [([band]+[ph.calc_mag(sp, band, system) for system in systems]) for band in bands]
    >>> print(tabulate.tabulate(rows, ["band"]+systems))
    band        stdflux          ab    vega
    ------  -----------  ----------  ------
    U        0.00572505   0.761594       -0
    B        0.0696287   -0.10383        -0
    V        0.0218067    0.0191189      -0
    R        0.0359559    0.214645       -0
    I        0.0661095    0.449825       -0
    J       -0.0150993    0.874666       -0
    H        0.0315447    1.34805        -0
    K        0.0246046    1.85948        -0
    """

    return calculate_magnitude(sp, bp, system, zero_point, flag_force_band_range)["cmag"]


def calculate_magnitude(sp, bp, system="stdflux", zero_point=0., flag_force_band_range=False):
    """
    Calculates magnitude from a Spectrum object.

    Args:
        sp: `f311.filetypes.Spectrum` instance. **flux unit** must be ``erg/cm**2/s/Hz`` aka "Fnu"
        bp: Bandpass object, or string in "UBVRIYJHKLMNQ". How it works:

            - If string in "UBVRI", creates a UBVTabular Bandpass object;
            - If string otherwise, creates a UBVParametric object.

        system: reference magnitude system. Possible values:

            - ``"stdflux"``: literature reference values for bands U,B,V,R,I,J,H,K only
            - ``"vega"``: uses the Vega star spectrum as a reference
            - ``"ab"``: AB[solute] magnitude system

        zero_point: subtracts this value from the calculated magnitude to implement some desired
                    correction.

        flag_force_band_range: this flag has effect when the spectrum does not completely overlap
            the bandpass filter. How it works:

            - ``False`` (default): restricts the weighted mean flux calculation to the overlap
              range between the spectrum and the filter
            - ``True``: zero-fill the spectrum to overlap the filter range completely

    Returns:
        dict: dictionary with the following keys:

            - ``"calc_l0"``: lower edge of wavelength interval considered,
            - ``"calc_lf"``: upper edge of wavelength interval considered,
            - ``"filtered_sp"``: filtered spectrum
            - ``"filtered_sp_area"``: area of filtered spectrum within [calc_l0, calc_lf]
            - ``"weighted_mean_flux"``: weighted mean of flux; weights are band values
            - ``"zero_flux"``: flux value for which magnitude is zero
            - ``"cmag"``: calculated magnitude

    Example:

    >>> from f311 import physics as ph
    >>> ph.calculate_magnitude(ph.get_vega_spectrum(), "U", "stdflux", 0, False)

    """

    bp = get_ubv_bandpass(bp)

    # # Determines areas
    filtered_sp = sp * bp
    if flag_force_band_range:
        calc_l0, calc_lf = bp.l0, bp.lf
    else:
        calc_l0, calc_lf = max(bp.l0, sp.l0), min(bp.lf, sp.lf)
    band_area = bp.area(calc_l0, calc_lf)
    # Note: discarding zeroes before integrating would make very little difference in time:
    #       ~47.5 against ~49.6 for the Vega spectrum with 8827 points
    filtered_sp_area = np.trapz(filtered_sp.y, filtered_sp.x)

    zero_flux = get_zero_flux(bp, system)

    weighted_mean_flux = filtered_sp_area/band_area
    cmag = -2.5 * np.log10(weighted_mean_flux / zero_flux) - zero_point

    ret = collections.OrderedDict((
    ("bp", bp),
    ("calc_l0", calc_l0),
    ("calc_lf", calc_lf),
    ("filtered_sp", filtered_sp),
    ("filtered_sp_area", filtered_sp_area),
    ("weighted_mean_flux", weighted_mean_flux),
    ("zero_flux", zero_flux),
    ("cmag", cmag),
    ))
    # if system == "vega":
    #     ret["filtered_vega_sp"] = filtered_vega_sp
    return ret




def flux_to_mag(flux, bp, system="stdflux", zero_point=0.):
    """
    Calculates magnitude for a single scalar flux value

    Args:
        flux: float (erg/cm**2/s/Hz), of Spectrum instance
        bp, system, zero_point: see calculate_magnitude()

    Returns: float
    """
    from f311 import physics as ph

    if isinstance(flux, ft.Spectrum):
        if flux.yunit != ph.fnu:
            raise ValueError("Spectrum y-unit must be '{}', not '{}'".format(ph.fnu, flux.yunit))
        flux = flux.y
    zero_flux = get_zero_flux(bp, system)
    return -2.5 * np.log10(flux / zero_flux) - zero_point


def get_zero_flux(bp, system="stdflux"):
    """
    Returns flux (erg/cm**2/s/Hz) for which magnitude is zero

    Args:
        bp: Bandpass object, or band name, e.g., "U"
        system: {"stdflux", "ab", "vega"} reference magnitude system

    For more on arguments, see calculate_magnitude()

    Returns: float
    """

    bp = __get_ubv_bandpass(bp)

    if system == "stdflux":
        if bp.name not in STDFLUX:
            raise ValueError("No standard flux for band '{}'".format(bp.name))
        zero_flux = STDFLUX[bp.name]
    elif system == "ab":
        zero_flux = 3631e-23
    elif system == "vega":
        vega_sp = __get_vega_spectrum()
        filtered_vega_sp = vega_sp * bp
        zero_flux = np.trapz(filtered_vega_sp.y, filtered_vega_sp.x) / bp.area(bp.l0, bp.lf)
    else:
        raise ValueError("Invalid reference magnitude system: '{0!s}'".format(system))
    return zero_flux


def mag_to_flux(mag, bp, system="stdflux"):
    """Inverse of calc_mag()"""
    zero_flux = get_zero_flux(bp, system)
    return zero_flux*10**(-.4*mag)


__vega_spectrum = None
def __get_vega_spectrum():
    """Returns spectrum of Vega loaded internally (always the same object)"""
    global __vega_spectrum
    if __vega_spectrum is None:
        __vega_spectrum = __get_new_vega_spectrum()
    return __vega_spectrum


def __get_new_vega_spectrum():
    from f311 import physics as ph
    return ft.load_spectrum(a99.get_path("data", "pysynphot-vega-fnu.xy", module=ph))


def get_vega_spectrum():
    """Returns a spectrum of the Vega star

    Creates a new `f311.filetypes.Spectrum` object at every call

    Returns:
        `f311.filetypes.Spectrum`: spectrum
    """
    return __get_new_vega_spectrum()


class Bandpass(object):
    """
    Wavelength filter band, with class tools

    This class is kept clean whereas UBVRIBands has examples and deeper documentation on parameters

    Args:
        tabular: ((wl, y), ...), 0 <= y <= 1
        parametric: ((wl, fwhm), ...)
        ref_mean_flux: reference mean flux passing through filter at magnitude 0 in Jy units
    """

    @property
    def l0(self):
        return self._get_l0()

    @property
    def lf(self):
        return self._get_lf()

    #     ****
    def __init__(self, name):
        self.name = name


    def _get_l0(self):
        raise NotImplementedError()


    def _get_lf(self):
        raise NotImplementedError


    def __mul__(self, other):
        raise TypeError("Bandpass left multiplication not defined")


    def __rmul__(self, other):
        """Right multiplication accepts Spectrum or tuple:(wave, flux)"""

        if isinstance(other, ft.Spectrum):
            out = copy.deepcopy(other)
            x, y = out.x, out.y
        elif isinstance(other, tuple) and len(other) == 2 and isinstance(other[0], np.ndarray) and \
             isinstance(other[1], np.ndarray) and len(other[0]) == len(other[1]):
            flag_spectrum = False
            out = copy.deepcopy(other)
            x, y = out
        else:
            raise TypeError("Invalid argument: "+str(other))

        # Overlap between bandpass filter and spectrum
        l0, lf = max(self.l0, x[0]), min(self.lf, x[-1])
        # Spectrum point indexes corresponding to this overlap (boolean mask)
        mask = np.logical_and(x >= l0, x <= lf)
        # Multiplies by filter
        y[mask] *= self.ufunc()(x[mask])
        # Points outside filter will be zero
        y[np.logical_not(mask)] = 0.
        return out


    def ufunc(self, flag_force_parametric=False):
        raise NotImplementedError()


    def area(self, l0, lf):
        """
        Calculates area (unit: a.u.*angstrom) under given range [l0, lf]
        Args:
            l0: lower edge of range
            lf: upper edge of range
        """
        # Calculates number of points as a fraction of REF_NUM_POINTS, minimum 10 points
        num_points = max(10, int((lf - l0) / (self.lf - self.l0) * _REF_NUM_POINTS))
        x = np.linspace(l0, lf, num_points)
        area = np.trapz(self.ufunc()(x), x)
        return area


class UBVTabulated(Bandpass):
    """
    Tabular filter

    Args:
        name: band name. Choices: U,B,V,R,I
    """

    # Tabular data for filters U,B,V,R,I
    # Michael Bessel 1990
    # Taken from http://spiff.rit.edu/classes/phys440/lectures/filters/filters.html
    DATA = collections.OrderedDict((
    ("U", ((3000, 0.00),  (3050, 0.016), (3100, 0.068), (3150, 0.167), (3200, 0.287), (3250, 0.423), (3300, 0.560),
           (3350, 0.673), (3400, 0.772), (3450, 0.841), (3500, 0.905), (3550, 0.943), (3600, 0.981), (3650, 0.993),
           (3700, 1.000), (3750, 0.989), (3800, 0.916), (3850, 0.804), (3900, 0.625), (3950, 0.423), (4000, 0.238),
           (4050, 0.114), (4100, 0.051), (4150, 0.019), (4200, 0.000))),
    ("B", ((3600, 0.0), (3700, 0.030), (3800, 0.134), (3900, 0.567), (4000, 0.920), (4100, 0.978), (4200, 1.000),
           (4300, 0.978), (4400, 0.935), (4500, 0.853), (4600, 0.740), (4700, 0.640), (4800, 0.536), (4900, 0.424),
           (5000, 0.325), (5100, 0.235), (5200, 0.150), (5300, 0.095), (5400, 0.043), (5500, 0.009), (5600, 0.0))),
    ("V", ((4700, 0.000), (4800, 0.030), (4900, 0.163), (5000, 0.458), (5100, 0.780), (5200, 0.967), (5300, 1.000),
          (5400, 0.973), (5500, 0.898), (5600, 0.792), (5700, 0.684), (5800, 0.574), (5900, 0.461), (6000, 0.359),
          (6100, 0.270), (6200, 0.197), (6300, 0.135), (6400, 0.081), (6500, 0.045), (6600, 0.025), (6700, 0.017),
          (6800, 0.013), (6900, 0.009), (7000, 0.000))),
    ("R", ((5500, 0.0), (5600, 0.23), (5700, 0.74), (5800, 0.91), (5900, 0.98), (6000, 1.000), (6100, 0.98),
           (6200, 0.96), (6300, 0.93), (6400, 0.90), (6500, 0.86), (6600, 0.81), (6700, 0.78), (6800, 0.72),
           (6900, 0.67), (7000, 0.61), (7100, 0.56), (7200, 0.51), (7300, 0.46), (7400, 0.40), (7500, 0.35),
           (8000, 0.14), (8500, 0.03), (9000, 0.00))),
    ("I", ((7000, 0.000), (7100, 0.024), (7200, 0.232), (7300, 0.555), (7400, 0.785), (7500, 0.910), (7600, 0.965),
           (7700, 0.985), (7800, 0.990), (7900, 0.995), (8000, 1.000), (8100, 1.000), (8200, 0.990), (8300, 0.980),
           (8400, 0.950), (8500, 0.910), (8600, 0.860), (8700, 0.750), (8800, 0.560), (8900, 0.330), (9000, 0.150),
           (9100, 0.030), (9200, 0.000)))
    ))

    def __init__(self, name):
        if name not in self.DATA:
            raise ValueError("Invalid band name, choices are ".format(*str(self.DATA.keys())))
        Bandpass.__init__(self, name)
        self.name = name
        self.x, self.y = zip(*self.DATA[name])

    def __repr__(self):
        return "UBVTabulated('{0!s}')".format(self.name)

    def _get_l0(self):
        return self.x[0]

    def _get_lf(self):
        return self.x[-1]

    def ufunc(self):
        return interp1d(self.x, self.y, kind='linear', bounds_error=False, fill_value=0)


class UBVParametric(Bandpass):
    """
    Parametric Gaussian filter

    Args:
        name: band name. Choices: U,B,V,R,I,Y,J,H,K,L,M,N,Q
        num_stds=3: number of standard deviations to left and right of midpoint to consider as
            band limits. Does not affect self.ufunc()
    """

    # Values taken from https://en.wikipedia.org/wiki/Photometric_system
    X0_FWHM = collections.OrderedDict((
    ("U", (3650., 660.)),
    ("B", (4450., 940.)),
    ("V", (5510., 880.)),
    ("R", (6580., 1380.)),
    ("I", (8060., 1490.)),
    ("Y", (10200., 1200.)),
    ("J", (12200., 2130.)),
    ("H", (16300., 3070.)),
    ("K", (21900., 3900.)),
    ("L", (34500., 4720.)),
    ("M", (47500., 4600.)),
    ("N", (105000., 25000.)),
    ("Q", (210000., 58000.))
    ))

    def __init__(self, name, num_stds=3):
        if name not in self.X0_FWHM:
            raise ValueError("Invalid band name, choices are ".format(*str(self.X0_FWHM.keys())))
        Bandpass.__init__(self, name)
        self.x0, self.fwhm = self.X0_FWHM[name]
        self.num_stds = num_stds

        std = self.fwhm * (1. / np.sqrt(8 * np.log(2)))
        self._l0, self._lf = self.x0 - num_stds * std, self.x0 + num_stds * std

    def __repr__(self):
        return "UBVParametric('{0!s}', {1:d})".format(self.name, self.num_stds)

    def _get_l0(self):
        return self._l0

    def _get_lf(self):
        return self._lf

    def ufunc(self):
        return _ufunc_gauss(self.x0, self.fwhm)


def _ufunc_gauss(x0, fwhm):
    """
    Returns Gaussian function (callable) that works as a numpy ufunc

    Args:
        x0: maximum value, where the function evaluates to 1.
        fwhm: "Full-Width at Half-Maximum"

    Reference: https://en.wikipedia.org/wiki/Gaussian_function
    """
    K = 4 * np.log(2) / fwhm ** 2
    def f(x):
        return np.exp(-(x - x0) ** 2 * K)
    return f


# Standard flux, according to several references
#
# TODO get references: Bessel etc
#
# values taken from https://en.wikipedia.org/wiki/Apparent_magnitude
# I- and J-band values agree with Evans, C.J., et al., A&A 527(2011): A50.
#
# Unit is erg/cm**2/s/Hz
STDFLUX = collections.OrderedDict((
("U", 1.81e-20),
("B", 4.26e-20),
("V", 3.64e-20),
("R", 3.08e-20),
("I", 2.55e-20),
("J", 1.60e-20),
("H", 1.08e-20),
("K", 0.67e-20),
))


def __get_ubv_bandpass(bp):
    """Internal function to convert string to Bandpass, or return the bp if already a Bandpass"""
    if isinstance(bp, Bandpass):
        pass
    elif isinstance(bp, str):
        if bp in "UBVRI":
            bp = UBVTabulated(bp)
        else:
            bp = UBVParametric(bp)
    else:
        raise ValueError("Invalid value for argument 'bandpass': {0!s}".format(str(bp)))
    return bp
