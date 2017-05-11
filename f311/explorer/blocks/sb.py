__all__ = ["SB_Rubberband", "SB_AddNoise", "SB_FNuToFLambda", "SB_FLambdaToFNu", "SB_ElementWise",
           "SB_Extend", "SB_Cut", "SB_Normalize", "SB_ConvertYUnit", "SB_Add", "SB_Mul",
           "SB_MulByLambda", "SB_DivByLambda"]


import numpy as np
import a99
import copy
from . import SpectrumBlock
import astropy.units as u
from ... import physics as ph
from .. import basic

class SB_Rubberband(SpectrumBlock):
    """
    Convex polygonal line (aka "rubberband")

    Args:
        flag_upper=True: whether to stretch rubberband from above the
            spectrum; otherwise, stretches line from below

    Stretches a polygonal line from below/above the spectrum. The vertices of this multi-segment
    line will touch "troughs" of the spectrum without crossing the spectrum

    This was inspired on -- but is not equivalent to -- OPUS Rubberband baseline correction [1].
    However, this one is parameterless, whereas OPUS RBBC asks for a number of points

    References:
        [1] Bruker Optik GmbH, OPUS 5 Reference Manual. Ettlingen: Bruker, 2004.
    """

    def __init__(self, flag_upper=True):
        SpectrumBlock.__init__(self)
        # Upper or lower rubberband
        self.flag_upper = flag_upper

    def _do_use(self, inp):
        output = self._new_output()
        y = inp.y
        if self.flag_upper:
            y = -y
        output.y = basic.rubberband(y)
        if self.flag_upper:
            output.y = -output.y
        return output


class SB_AddNoise(SpectrumBlock):
    """
    Adds normally distributed (Gaussian) random noise

    Args:
        std=1.: standard deviation of Gaussian noise
    """
    def __init__(self, std=1.):
        SpectrumBlock.__init__(self)
        # Standard deviation of noise
        self.std = std

    def _do_use(self, inp):
        n = len(inp)
        output = self._new_output()
        output.y = np.copy(inp.y) + np.random.normal(0, self.std, n)
        return output


class SB_ElementWise(SpectrumBlock):
    """
    Applies specified function to spectrum flux

    Args:
        func: a function that takes a vector (_i.e._, NumPy 1-D array) as input. It must return
            vector of same dimension as input.NumPy ufunc's are suited for this.
            Examples:
                np.square
                np.exp
            It also be a lambda using list comprehension, for example:
                lambda v: [x**2 for x in v]
    """

    def __init__(self, func):
        SpectrumBlock.__init__(self)
        self.func = func

    def _do_use(self, inp):
        output = self._new_output()
        output.wavelength = np.copy(inp.wavelength)
        output.flux = self.func(inp.flux)
        if len(output.flux) != len(output.wavelength):
            raise RuntimeError(
                "func returned vector of length %d, but should be %d" % (len(output.flux), len(output.wavelength)))
        if not isinstance(output.flux, np.ndarray):
            output.flux = np.array(output.flux)
        return output


class SB_Extend(SpectrumBlock):
    """
    Extends to left and/or right side

    Args:
        fraction: amount relative to number of points. Note that this
                    applies individually to left and right (see below)
        flag_left: whether to extend by fraction to left
        flag_right: whether to extend by fraction to right
        fill_mode='poly_baseline': how to fill the new points. Valid values:
            'poly_baseline': The y-value (left/right) to use is found by using a "coarse"
                                2nd-order polynomial baseline. The baseline is "coarse" because it
                                does not allow for many iterations until the baseline is found
            'zero': Fills with zero

    Examples:
        SB_Extend(.1, True, True)  # if original has 100 points, resulting will have 120 points

        SB_Extend(.1, True, False)  # if original has 100 points, resulting will have 110 points
    """

    def __init__(self, fraction=.1, flag_left=True, flag_right=False, fill_mode='poly_baseline'):
        SpectrumBlock.__init__(self)
        self.fraction = fraction
        self.flag_left = flag_left
        self.flag_right = flag_right
        if not fill_mode in ('poly_baseline', 'zero'):
            raise RuntimeError("Invalid fill mode: '%s'" % fill_mode)
        self.fill_mode = fill_mode

    def _do_use(self, inp):
        from f311 import explorer as ex

        # TODO work with delta_lambda not constant
        output = self._copy_input(inp)

        if not (self.flag_left or self.flag_right):
            return output
        num_add = int(self.fraction*len(output.wavelength))
        if num_add <= 0:
            return output

        x_left, x_right, y_left, y_right = np.array([]), np.array([]), np.array([]), np.array([])

        if self.fill_mode == 'poly_baseline':
            baseline = -ex.poly_baseline(-output.y, 2, maxit=15)
            fill_l = baseline[0]
            fill_r = baseline[-1]
        elif self.fill_mode == 'zero':
            fill_l = 0
            fill_r = 0
        else:
            raise RuntimeError("Invalid fill mode: '%s'" % self.fill_mode)

        if self.flag_left:
            x_left = np.arange(num_add)*output.delta_lambda+(output.x[0]-output.delta_lambda*num_add)
            y_left = np.ones(num_add)*fill_l

        if self.flag_right:
            x_right = np.arange(num_add) * output.delta_lambda + (output.x[-1] + output.delta_lambda)
            y_right = np.ones(num_add)*fill_r

        output.x = np.concatenate((x_left, output.x, x_right))
        output.y = np.concatenate((y_left, output.y, y_right))

        return output


class SB_Cut(SpectrumBlock):
    """
    Cuts spectrum given a wavelength interval

    Args:
        l0: initial wavelength
        lf: final wavelength
    """

    def __init__(self, l0, lf):
        SpectrumBlock.__init__(self)
        if l0 >= lf:
            raise ValueError("l0 must be lower than lf")
        self.l0 = l0
        self.lf = lf

    def __repr__(self):
        return "SB_Cut({}, {})".format(self.l0, self.lf)

    def _do_use(self, inp):
        idx0 = np.argmin(np.abs(inp.x - self.l0))
        idx1 = np.argmin(np.abs(inp.x - self.lf))
        out = self._copy_input(inp)
        out.x = out.x[idx0:idx1]
        out.y = out.y[idx0:idx1]
        return out


class SB_Normalize(SpectrumBlock):
    """
    Normalizes spectrum according to specified method

    Args:
        method --
            "01": normalizes between 0 and 1
            "1": scales to have maximum at 1, keeping the 0 where it is
    """

    def __init__(self, method="01"):
        SpectrumBlock.__init__(self)
        choices = ["01", "1"]
        if not method in choices:
            raise ValueError("Invalid normalization method; choices: %s" % str(choices))
        self.method = method

    def __repr__(self):
        return "SB_Normalize('{}')".format(self.method)

    def _do_use(self, inp):
        out = self._copy_input(inp)
        if self.method == "01":
            miny, maxy = np.min(out.y), np.max(out.y)
            if miny == maxy:
                raise RuntimeError("Cannot normalize, y-span is ZERO")
            out.y = (out.y - miny) / (maxy - miny)

        elif self.method == "1":
            maxy = np.max(out.y)
            out.y = out.y / maxy
        return out


# # Temporarily suspended (changing x-axis has implications in SpectrumList.wavelength vector
#
# class SB_ConvertXUnit(SpectrumBlock):
#     """
#     Converts x-axis unit
#
#     Args:
#         new_unit: astropy.units.unit or str
#     """
#
#     def __init__(self, new_unit):
#         SpectrumBlock.__init__(self)
#         self.unit = u.Unit(new_unit)
#
#     def __repr__(self):
#         return "{}({})".format(self.__class__.__name__, repr(self.unit))
#
#     def _do_use(self, inp):
#         qty = inp.x * inp.xunit
#         out = self._copy_input(inp)
#         out.x = qty.to(self.unit).value
#         out.unit = copy.deepcopy(self.unit)
#         return out


class SB_ConvertYUnit(SpectrumBlock):
    """
    Converts y-axis unit

    Args:
        new_unit: astropy.units.unit or str
    """

    def __init__(self, new_unit):
        SpectrumBlock.__init__(self)
        self.unit = u.Unit(new_unit)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.unit))

    def _do_use(self, inp):
        # qty = inp.y * inp.yunit
        out = self._copy_input(inp)
        out.y = out.yunit.to(self.unit, out.y, equivalencies=u.spectral_density(out.xunit, out.x))
        out.yunit = copy.deepcopy(self.unit)
        return out


class SB_FNuToFLambda(SB_ConvertYUnit):
    """
    Flux-nu to flux-lambda conversion. Assumes the wavelength axis is in angstrom

    Formula:
        f_lambda = f_nu*(nu/lambda) = f_nu*c/lambda**2

        where
            lambda is the wavelength in cm,
            c is the speed of light in cm/s
            f_lambda has irrelevant unit for this purpose
    """

    def __init__(self):
        SB_ConvertYUnit.__init__(self, ph.flambda)


class SB_FLambdaToFNu(SB_ConvertYUnit):
    """
    Flux-nu to flux-lambda conversion. Assumes the wavelength axis is in angstrom

    Formula:
        f_nu = f_lambda*(lambda/nu) = f_lambda*lambda**2/c
    """
    def __init__(self):
        SB_ConvertYUnit.__init__(self, ph.fnu)



class SB_Mul(SpectrumBlock):
    """
    Multiplies y-values by constant value

    Args:
        value
    """

    def __init__(self, value=1.):
        SpectrumBlock.__init__(self)
        self.value = value

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.value))

    def _do_use(self, inp):
        # qty = inp.y * inp.yunit
        out = self._copy_input(inp)
        out.y *= self.value
        return out


class SB_Add(SpectrumBlock):
    """
    Adds constant value to y-values

    Args:
        value
    """

    def __init__(self, value=0.):
        SpectrumBlock.__init__(self)
        self.value = value

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.value))

    def _do_use(self, inp):
        out = self._copy_input(inp)
        out.y += self.value
        return out


class SB_MulByLambda(SpectrumBlock):
    """Multiplies each y-point by its wavelength"""

    def _do_use(self, inp):
        out = self._copy_input(inp)
        out.y *= out.x
        return out


class SB_DivByLambda(SpectrumBlock):
    """Divides each y-point by its wavelength"""

    def _do_use(self, inp):
        out = self._copy_input(inp)
        out.y /= out.x
        return out

