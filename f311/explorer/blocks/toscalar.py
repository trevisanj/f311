__all__ = ["ToScalar_SNR", "ToScalar_Magnitude", "ToScalar_UseNumPyFunc"]


from .basic import ToScalar
import numpy as np
import f311.physics as ph

class ToScalar_SNR(ToScalar):
    """
    Calculates Signal-to-noise ratio (SNR) using a part of the "signal" (i.e. the spectrum)

    Formula: SNR = sqrt((y_**2)) / std(y_),
             where:
                 y_ is the  slice of of the spectrum flux vector within the range [llzero, llfin];
                 the numerator is the RMS value of y_

    **Note** this has been tested to be consistent with IRAF SNR calculation

    **Note** It is assumed that the "signal" is *stationary* within [llzero, llfin]
    meaning that the mean and variance of the "signal" is the same for all points within
    this region (more precisely "weak-sense stationary"
    (https://en.wikipedia.org/wiki/Stationary_process#Weak_or_wide-sense_stationarity))
    """

    def __init__(self, llzero, llfin):
        ToScalar.__init__(self)
        self.llzero = llzero
        self.llfin = llfin

    def _do_use(self, inp):
        x = inp.x
        y = inp.y
        signal = y[np.logical_and(x >= self.llzero, x <= self.llfin)]

        a = np.sqrt(np.mean(signal**2))
        b = np.std(signal)

        if a == 0 and b == 0:
            output = float("nan")
        elif b == 0:
            output = float("inf")
        else:
            output = a/b
        return output


class ToScalar_Magnitude(ToScalar):
    """
    Calculates the magnitude of a spectrum

        Args:
            band_name: U/B/V/R/I/Y/J/H/K/L/M/N/Q
            system: reference magnitude system.
                Choices:
                    "stdflux": literature reference values for bands U,B,V,R,I,J,H,K only
                    "vega": uses the Vega star spectrum as a reference
                    "ab": AB[solute] magnitude system
            zero_point: subtracts this value from the calculated magnitude to implement some desired
                        correction.
            flag_force_band_range: (default: False) if set, will consider that the spectrum
                                   extends over the full range of the band even if it is narrower
                                   than that
    """


    def __init__(self, band_name, system="stdflux", zero_point=0., flag_force_band_range=False):
        ToScalar.__init__(self)
        self.band_name = band_name
        self.system = system
        self.zero_point = zero_point
        self.flag_force_band_range = flag_force_band_range

    def _do_use(self, inp):
        return ph.calc_mag(inp, self.band_name, self.system, self.zero_point,
                           self.flag_force_band_range)


class ToScalar_UseNumPyFunc(ToScalar):
    """
    Reduces spectrum y-vector to scalar using a numpy function, e.g., np.mean(), np.std()
    """

    def __init__(self, func=np.mean):
        ToScalar.__init__(self)
        self.func = func

    def _do_use(self, inp):
        out = self.func(inp.y)
        if isinstance(out, np.ndarray):
            try:
                # tries nice string representation;
                s = self.func.__name__
            except:
                # if fails, goes for generic string conversion
                s = str(self.func)
            raise RuntimeError("Function '{}' does not evaluate to scalar".format(s))
        return out