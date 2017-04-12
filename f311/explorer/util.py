"""
Miscellanea routines that depend on other modules and sub-packages.

Rule: only 'gui/' modules can import util!!!
"""

import numpy as np
import copy
from .. import physics as ph
import a99

__all__ = ["cut_spectrum", "crop_splist",]
def cut_spectrum(sp, l0, lf):
    """
    Cuts spectrum given a wavelength interval, leaving origina intact

    Args:
        sp: Spectrum instance
        l0: initial wavelength
        lf: final wavelength

    Returns:
        Spectrum: cut spectrum
    """

    if l0 >= lf:
        raise ValueError("l0 must be lower than lf")
    idx0 = np.argmin(np.abs(sp.x - l0))
    idx1 = np.argmin(np.abs(sp.x - lf))
    out = copy.deepcopy(sp)
    out.x = out.x[idx0:idx1]
    out.y = out.y[idx0:idx1]
    return out


def get_rgb(self, visible_range=None, method=0):
    """Takes weighted average of rainbow colors RGB's

    Args:
        visible_range=None: if passed, affine-transforms the rainbow colors
        method --
          0: rainbow colors
          1: RGB
    """

    if len(visible_range) < 2:
        raise RuntimeError("Invalid visible range: {0!s}".format(visible_range))
    if visible_range[1] <= visible_range[0]:
        raise RuntimeError(
            "Second element of visible range ({0!s}) must be greater than first element".format(
                visible_range))

    if method == 1:
        # new color system splitting visible range in three
        dl = float(visible_range[1] - visible_range[0]) / 3
        ranges = np.array(
            [[visible_range[0] + i * dl, visible_range[0] + (i + 1) * dl] for i in range(3)])
        colors = np.array([(0., 0., 1.), (0., 1., 0.), (1., 0., 0.)])  # blue, green, red

        tot_area, tot_sum = 0., np.zeros(3)
        for color, range_ in zip(colors, ranges):
            b = np.logical_and(self.x >= range_[0], self.x <= range_[1])
            area = np.sum(self.y[b])
            tot_area += area
            tot_sum += color * area
        if tot_area == 0.:
            tot_area = 1.
        ret = tot_sum / tot_area
        return ret

    elif method == 0:
        tot_area, tot_sum = 0., np.zeros(3)

        def ftrans(x):
            return x

        if visible_range:
            ll0 = ph.rainbow_colors[0].l0
            llf = ph.rainbow_colors[-1].lf
            ftrans = lambda lold: visible_range[0] + (visible_range[1] - visible_range[0]) / (
            llf - ll0) * (lold - ll0)

        for color in ph.rainbow_colors:
            b = np.logical_and(self.x >= ftrans(color.l0), self.x <= ftrans(color.lf))
            area = np.sum(self.y[b])
            tot_area += area
            tot_sum += color.rgb * area
        if tot_area == 0.:
            tot_area = 1.
        ret = tot_sum / tot_area
        return ret
    else:
        raise RuntimeError("Unknown method: {0!s}".format(method))


def crop_splist(splist, lambda0=None, lambda1=None):
    """
    Cuts all spectra in SpectrumList

    **Note** lambda1 **included** in interval (not pythonic).
    """
    if len(splist.spectra) == 0:
        raise RuntimeError("Need at least one spectrum added in order to crop")

    if lambda0 is None:
        lambda0 = splist.wavelength[0]
    if lambda1 is None:
        lambda1 = splist.wavelength[-1]
    if not (lambda0 <= lambda1):
        raise RuntimeError('lambda0 must be <= lambda1')

    if not any([lambda0 != splist.wavelength[0], lambda1 != splist.wavelength[-1]]):
        return

    for i in range(len(splist)):
        sp = cut_spectrum(splist.spectra[i], lambda0, lambda1)
        if i == 0:
            n = len(sp)
            if n < 2:
                raise RuntimeError(
                    "Cannot cut, spectrum will have %d point%s" % (n, "" if n == 1 else "s"))
        splist.spectra[i] = sp

    splist.__update()
