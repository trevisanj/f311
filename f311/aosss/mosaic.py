"""
Spectrograph modes specifications
"""

from a99 import AttrsPart


class SpectrographMode(AttrsPart):
    """
    Spectrograph mode specification

    Args:
        name: name of spectrograph mode
        abbreviation: abbreviation of spectrograph mode
        aperture: aperture in (arcsec)
        multiplex: maximum number of simultaneous objects being observed (unitless)
        wavelength_range: [lambda_min, lambda_max] (angstrom)
        resolving_power: lambda/delta_lambda (unitless)
        fov: field-of-view (arcmin**2)
        flag_glao: whether or not Ground-Layer Adaptive Optics is available for this mode
        flag_moao: whether of not Multi-Object Adaptive Optics is available for this mode
        pixel_size: spatial pixel size
    """

    attrs = ["name", "abbreviation", "aperture", "multiplex", "wavelength_range", "resolving_power",
             "fov", "flag_glao", "flag_moao", "pixel_size"]

    def __init__(self, name="", abbreviation="", aperture=0., multiplex=0.,
                 wavelength_range=(0., 0.), resolving_power=0., fov=0., flag_glao=False,
                 flag_moao=False, pixel_size=0.):
        AttrsPart.__init__(self)

        self.name = name
        self.abbreviation = abbreviation
        self.aperture = aperture
        self.multiplex = multiplex
        self.wavelength_range = wavelength_range
        self.resolving_power = resolving_power
        self.fov = fov
        self.flag_glao = flag_glao
        self.flag_moao = flag_moao
        self.pixel_size = pixel_size



modes = [
    SpectrographMode(name="High Multiplex Mode - Visible",
                     abbreviation="HMM-Vis",
                     aperture=.9,
                     multiplex=200,
                     wavelength_range=(4000., 7000.),
                     resolving_power=15000.,
                     fov=40.,
                     flag_glao=True,
                     flag_moao=False
                    ),
    SpectrographMode(name="High Multiplex Mode - NIR",
                     abbreviation="HMM-NIR",
                     aperture=.6,
                     multiplex=200,
                     wavelength_range=(7000., 18000.),
                     resolving_power=5000.,
                     fov=40.,
                     flag_glao=True,
                     flag_moao=False
                     ),
    SpectrographMode(name="High Definition Mode (essential)",
                     abbreviation="HDM (essential)",
                     aperture=2.,
                     multiplex=10,
                     wavelength_range=(10000., 18000.),
                     resolving_power=5000.,
                     fov=40.,
                     flag_glao=True,
                     flag_moao=True,
                     pixel_size=80.,
                     ),
    SpectrographMode(name="High Definition Mode (desirable)",
                     abbreviation="HDM (desirable)",
                     aperture=2.,
                     multiplex=10,
                     wavelength_range=(8000., 25000.),
                     resolving_power=15000.,
                     fov=40.,
                     flag_glao=True,
                     flag_moao=True,
                     pixel_size=40.,
                     ),
    SpectrographMode(name="Inter-Galactic Mode (essential)",
                     abbreviation="IGM (essential)",
                     aperture=3.,
                     multiplex=30,
                     wavelength_range=(4000., 8000.),
                     resolving_power=3000.,
                     fov=40.,
                     flag_glao=True,
                     flag_moao=False,  # TODO not sure if MOAO is really not available in IGM
                     pixel_size=250.,
                     ),
    SpectrographMode(name="Inter-Galactic Mode (desirable)",
                     abbreviation="IGM (desirable)",
                     aperture=3.,
                     multiplex=30,
                     wavelength_range=(3700., 10000.),
                     resolving_power=5000.,
                     fov=40.,
                     flag_glao=True,
                     flag_moao=False,  # TODO not sure if MOAO is really not available in IGM
                     pixel_size=250.,
                     ),
    ]

