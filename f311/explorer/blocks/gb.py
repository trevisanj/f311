__all__ = ["GB_UseNumPyFunc", "GB_SNR"]


from .base import *
from . import sb
import a99
import aosss as ao


class GB_UseNumPyFunc(GroupBlock):
    """Output contains single spectrum whose y-vector is calculated using a numpy function

    The numpy function must be able to operate on the first axis, e.g., np.mean(), np.std()
    """

    def __init__(self, func=np.std):
        GroupBlock.__init__(self)
        self.func = func

    def _do_use(self, inp):
        output = self._new_output()
        sp = a99.Spectrum()
        sp.wavelength = np.copy(inp.wavelength)
        sp.flux = self.func(inp.matrix(), 0)
        if len(sp.flux) != len(sp.wavelength):
            raise RuntimeError("func returned vector of length %d, but should be %d" % (len(sp.flux), len(sp.wavelength)))
        output.add_spectrum(sp)
        return output


class GB_SNR(GroupBlock):
    """Calculates the GB_SNR(lambda) = Power_signal(lambda)/Power_noise(lambda)

    Arguments:
        continua -- SpectrumList containing the continua that will be used as the "signal" level.
                    If not passed, will be calculated from the input spectra using a SB_Rubberband(True) block

    References:
        [1] https://en.wikipedia.org/wiki/Signal_averaging
    """

    # TODO I think that it is more correct to talk about "continuum" not continua

    def __init__(self, continua=None):
        GroupBlock.__init__(self)
        self.continua = continua

    def _do_use(self, inp):
        if self.continua is None:
            continua = ao.SLB_UseSpectrumBlock(sb.SB_Rubberband(True)).use(inp)
        else:
            continua = self.continua
        cont_2 = ao.UseSpectrumBlock(sb.SB_ElementWise(np.square)).use(continua)  # continua squared
        mean_cont_2 = GB_UseNumPyFunc(np.mean).use(cont_2)
        var_spectra = GB_UseNumPyFunc(np.var).use(inp)
        output = self._new_output()
        sp = a99.Spectrum()
        sp.wavelength = np.copy(inp.wavelength)
        sp.flux = mean_cont_2.spectra[0].flux/var_spectra.spectra[0].flux
        output.add_spectrum(sp)
        return output
