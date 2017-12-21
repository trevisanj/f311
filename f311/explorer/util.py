"""
Miscellanea routines that depend on other modules and sub-packages.

Rule: only 'gui/' modules can import util!!!
"""

import numpy as np
import copy
import a99

__all__ = ["cut_spectrum", ]


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

