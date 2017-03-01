"""
Rainbow colors

Example:

>>> for color in rainbow_colors:
...     color
Color('Violet', [ 0.54509804  0.          1.        ], 4000.0, 3775.0, 4225.0)
Color('Indigo', [ 0.29411765  0.          0.50980392], 4450.0, 4225.0, 4600.0)
Color('Blue', [ 0.  0.  1.], 4750.0, 4600.0, 4925.0)
Color('Green', [ 0.  1.  0.], 5100.0, 4925.0, 5400.0)
Color('Yellow', [ 1.  1.  0.], 5700.0, 5400.0, 5800.0)
Color('Orange', [ 1.          0.49803922  0.        ], 5900.0, 5800.0, 6200.0)
Color('Red', [ 1.  0.  0.], 6500.0, 6200.0, 6800.0)

Example:

>>> import matplotlib.pyplot as plt
>>> for color in rainbow_colors:
...     _ = plt.fill_between([color.l0, color.lf], [1., 1.], color=color.rgb, label=color.name)
>>> _ = plt.legend(loc=0)
>>> _ = plt.xlabel('Wavelength (angstrom)')
>>> _ = plt.tight_layout()
>>> _ = plt.show()

"""


__all__ = ["Color", "rainbow_colors", "ncolors", "spectrum_to_rgb"]


from a99 import AttrsPart
import numpy as np


class Color(AttrsPart):
    """Definition of a color: name, RGB code, wavelength range"""

    attrs = ["name", "rgb", "clambda", "l0", "lf"]

    def __init__(self, name, rgb, clambda, l0=-1, lf=-1):
        AttrsPart.__init__(self)
        # Name of color
        self.name = name
        # (red, green, blue) tuple (numbers in [0, 1] interval)
        self.rgb = rgb
        # Central wavelength (angstrom)
        self.clambda = clambda
        # Initial wavelength (angstrom)
        self.l0 = l0
        # Final wavelength (angstrom)
        self.lf = lf

    def __repr__(self):
        return "Color('{}', {}, {}, {}, {})".format(self.name, self.rgb, self.clambda, self.l0, self.lf)


#: Rainbow colors
rainbow_colors = [Color("Violet", [139, 0, 255], 4000),
                  Color("Indigo", [75, 0, 130], 4450),
                  Color("Blue", [0, 0, 255], 4750),
                  Color("Green", [0, 255, 0], 5100),
                  Color("Yellow", [255, 255, 0], 5700),
                  Color("Orange", [255, 127, 0], 5900),
                  Color("Red", [255, 0, 0], 6500),
                  ]

# Calculates l0, lf
# rainbow_colors[0].l0 = 0.
# rainbow_colors[-1].lf = float("inf")
for c in rainbow_colors:
    c.clambda = float(c.clambda)
ncolors = len(rainbow_colors)
for i in range(1, ncolors):
    cprev, cnow = rainbow_colors[i-1], rainbow_colors[i]
    avg = (cprev.clambda + cnow.clambda) / 2
    cprev.lf = avg
    cnow.l0 = avg

    if i == 1:
        cprev.l0 = 2*cprev.clambda-cprev.lf
    if i == ncolors-1:
        cnow.lf = 2*cnow.clambda-cnow.l0
# converts RGB from [0, 255] to [0, 1.] interval
for c in rainbow_colors:
    c.rgb = np.array([float(x)/255 for x in c.rgb])


def spectrum_to_rgb(sp, visible_range=None, method=0):
    """Takes weighted average of rainbow colors RGB's

    Args:
        sp: Spectrum instance
        visible_range=None: if passed, affine-transforms the rainbow colors
        method:

            - ``0``: rainbow colors
            - ``1``: RGB (alternative method using red, green, blue only instead of full range of rainbow colors)

    Returns:
        3-element sequence where each element is in [0, 1] range

    Example:

    >>> import f311.physics as ph
    >>> vega = ph.get_vega_spectrum()
    >>> ph.spectrum_to_rgb(vega)
    array([  5.45057920e-01,   1.61124778e-05,   9.99930126e-01])
    """

    if visible_range is None:
        visible_range = min(sp.x), max(sp.x)

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
            ll0 = rainbow_colors[0].l0
            llf = rainbow_colors[-1].lf
            ftrans = lambda lold: visible_range[0] + (visible_range[1] - visible_range[0]) / (
            llf - ll0) * (lold - ll0)

        for color in rainbow_colors:
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
