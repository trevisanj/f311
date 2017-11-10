__all__ = ["FullCube"]


import a99
import numpy as np
from astropy.io import fits


@a99.froze_it
class FullCube(a99.AttrsPart):
    """
    X-Y-wavelength cube

    Based on IDL source file chris_J4000.pro

    Data is stored primarily in self.hdu, with a few other relevant attributes

    Notes on FITS HDU:
      - data is stored in reverse dimensions, i.e., (z, y, x)
      - CDELT1, CRVAL1 refer to x
      - CDELT2, CRVAL2 refer to y
      - CDELT3, CRVAL3 refer to z
    """

    attrs = ["hdu"]

    @property
    def flag_created(self):
        """Whether the data cube has already been created"""
        return self.hdu is not None

    @property
    def flag_wavelengthed(self):
        """Whether wavelength information is already present """
        return self.flag_created and self.hdu.header["CDELT3"] != -1

    def __init__(self, hdu=None):
        a99.AttrsPart.__init__(self)
        self.hdu = None  # PyFITS HDU object
        self.wavelength = None  # the wavelength axis (angstrom) (shared among all spectra in the cube)
        self.filename = None

        if hdu is not None:
            self.from_hdu(hdu)

    def from_hdu(self, hdu):
        """
        Sets self.hdu and with HDU object passed. Warning: may change HDU object.

        Default HDU headers:

            - CDELT1 defaults to 1
            - CDELT2 defaults to CDELT1
            - CRDELT3 defaults to 1
            - CRVAL3 defaults to 0
        """
        assert isinstance(hdu, fits.PrimaryHDU)

        # ensures all required headers are present
        keys = ["NAXIS1", "NAXIS2"]
        for key in keys:
            if key not in hdu.header:
                raise ValueError('Key "%s" not found in headers' % key)

        # 20171110 If the data is 2D, we make it 3D by assuming only one row in first dimension


        shape = hdu.data.shape

        if len(shape) == 2:
            a99.get_python_logger().info("HDU data is 2D, will add y axis with only one row to make it 3D")

            hdu.data = hdu.data.reshape((shape[0], 1, shape[1]))

            shape = hdu.data.shape

            _map = [("CRVAL3", lambda: hdu.header["CRVAL2"]),
                    ("CDELT3", lambda: hdu.header["CDELT2"]),
                    ("CDELT2", lambda: hdu.header["CDELT1"]),
                    ("CDELT1", lambda: 1),
                    ]


            # _map = [("NAXIS3", lambda: hdu.header["NAXIS2"]),
            #         ("NAXIS2", lambda: hdu.header["NAXIS1"]),
            #         ("NAXIS1", lambda: 1),
            #         ("CRVAL3", lambda: hdu.header["CRVAL2"]),
            #         ("CDELT3", lambda: hdu.header["CDELT2"]),
            #         ("CDELT2", lambda: hdu.header["CDELT1"]),
            #         ("CDELT1", lambda: 1),
            #         ]

            for key, f_value in _map:
                try:
                    hdu.header[key] = f_value()
                except KeyError:
                    a99.get_python_logger().warning("Trying to convert 2D to 3D: necessary header key missing: '{}'".format(key))


        if not "CDELT3" in hdu.header:
            a99.get_python_logger().warning("HDU lacks header 'CDELT3', assumed 1.0")
            hdu.header["CDELT3"] = 1.
        if not "CRVAL3" in hdu.header:
            a99.get_python_logger().warning("HDU lacks header 'CRVAL3', assumed 0.0")
            hdu.header["CRVAL3"] = 0.
        if not "CDELT1" in hdu.header:
            a99.get_python_logger().warning("HDU lacks header 'CDELT1', assumed 1.0")
            hdu.header["CDELT1"] = 1.0
        if not "CDELT2" in hdu.header:
            a99.get_python_logger().warning("HDU lacks header 'CDELT2', assumed value in 'CDELT1'")
            hdu.header["CDELT2"] = hdu.header["CDELT1"]
        if not "HRFACTOR" in hdu.header:
            hdu.header["HRFACTOR"] = 1.

        l0 = hdu.header["CRVAL3"]  # I think WC was adding this but changed ... +hdu.header["CDELT3"]
        delta_lambda = hdu.header["CDELT3"]
        nlambda = hdu.header["NAXIS3"]
        self.hdu = hdu

        self.set_wavelength(np.array([l0 + k * delta_lambda for k in range(0, nlambda)]))

    def __len__(self):
        raise NotImplementedError()

    def __repr__(self):
        return "Please implement FullCube.__repr__()"

    def create1(self, R, dims, hr_pix_size, hrfactor):
        """Creates FITS HDU, including the cube full with zeros

          dims: (nlambda, height, width)
        """
        cube = np.zeros(dims)
        hdu = fits.PrimaryHDU()
        hdu.header["CDELT1"] = hr_pix_size
        hdu.header["CDELT2"] = hr_pix_size
        hdu.header["CDELT3"] = -1.0  # this will become known then paint() is called for the first time
        hdu.header["CRVAL3"] = -1.0  # "
        hdu.header["HRFACTOR"] = hrfactor
        hdu.header["R"] = R
        hdu.data = cube
        self.hdu = hdu

    def get_spectrum(self, x, y):
        """
        Returns spectrum at coordinate x, y (copied vectors)

        **Note** coordinate (x=0, y=0) corresponds to lower left pixel of cube cross-section
        """
        import f311.filetypes as ft
        assert self.flag_wavelengthed

        sp = ft.Spectrum()
        sp.x = np.copy(self.wavelength)
        sp.y = np.copy(self.hdu.data[:, y, x])
        sp.more_headers["PIXEL-X"] = x  # why not
        sp.more_headers["PIXEL-Y"] = y
        return sp

    def set_wavelength(self, w):
        delta_lambda = w[1] - w[0]
        self.hdu.header["CDELT3"] = delta_lambda
        # dunno why the initial lambda must be one delta lambda lower than the initial lambda in the spectrum, but
        # this is how it was in the original
        self.hdu.header["CRVAL3"] = w[0] - delta_lambda
        self.wavelength = w
