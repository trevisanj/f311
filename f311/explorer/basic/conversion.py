"""
Basic routines, they don't use anything from parent module
"""


import numpy as np
import f311.physics as ph

__all__ = ["sparse_cube_to_colors", "spectrum_to_rgb"]

def sparse_cube_to_colors(scube, visible_range=None, flag_scale=False, method=0):
    """Returns a [nY, nX, 3] red-green-blue (0.-1.) matrix

    Args:
      visible_range=None: if passed, the true human visible range will be
                            affine-transformed to visible_range in order
                            to use the red-to-blue scale to paint the pixels
      flag_scale: whether to scale the luminosities proportionally
                    the weight for each spectra will be the area under the flux
      method: see f311.physics.spectrum_to_rgb()
    """
    im = np.zeros((scube.height, scube.width, 3))
    weights = np.zeros((scube.height, scube.width, 3))
    max_area = 0.
    for i in range(scube.width):
        for j in range(scube.height):
            sp = scube.get_pixel(i, j, False)
            if len(sp) > 0:
                im[j, i, :] = ph.spectrum_to_rgb(sp, visible_range, method)
                sp_area = np.sum(sp.y)
                max_area = max(max_area, sp_area)
                if flag_scale:
                    weights[j, i, :] = sp_area
    if flag_scale:
        weights *= 1. / max_area
        im *= weights
    return im


def spectrum_to_rgb(sp, visible_range=None, method=0):
    """Takes weighted average of rainbow colors RGB's

    Args:
        sp: f311.filetypes.Spectrum instance
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
            b = np.logical_and(sp.x >= range_[0], sp.x <= range_[1])
            area = np.sum(sp.y[b])
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
            b = np.logical_and(sp.x >= ftrans(color.l0), sp.x <= ftrans(color.lf))
            area = np.sum(sp.y[b])
            tot_area += area
            tot_sum += color.rgb * area
        if tot_area == 0.:
            tot_area = 1.
        ret = tot_sum / tot_area
        return ret
    else:
        raise RuntimeError("Unknown method: {0!s}".format(method))
