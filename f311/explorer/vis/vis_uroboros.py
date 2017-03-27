from ... import filetypes as ft
from .basic import Vis
import matplotlib.pyplot as plt
import a99
import numpy as np

__all__ = ["VisGalfitFig", "draw_15_tiles"]


# TODO setup image size

class VisGalfitFig(Vis):
    """Draw figure of 3 x 5 tiles"""

    input_classes = (ft.FileGalfit,)
    action = __doc__

    def _do_use(self, m):
        draw_15_tiles(m.hdulist)
        plt.show()


def draw_15_tiles(hdulist, image_width=1000):
    """Draws a new matplotilb figure and returns it

    The figure will contain 15 = 3*5 subplots

    Args:
        hdulist: object obtained using astropy.io.fits.open. This represents
                 a FITS file containing 20 frames.
                 Frames from 2nd to 16th will be used
        image_width=1000: image width in pixels

    Returns:
        matplotlib figure
    """


    fig = plt.figure()
    for i, hdu in enumerate(hdulist[1:16]):
        plt.subplot(3, 5, i + 1)  # 1 + i // 5, 1 + i % 5)

        # http://stackoverflow.com/questions/12998430/remove-xticks-in-a-matplot-lib-plot
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())

        im = hdu.data
        # Clips negative values
        im[im < 0] =  0
        # Transforms color values to something that will enhance small values
        image_data = np.power(im, 0.2)

        plt.imshow(image_data, cmap='gray')
        plt.ylim([0, image_data.shape[0] - 1])
        plt.ylim([0, image_data.shape[1] - 1])


    a99.set_figure_size(fig, image_width, image_width/5*3)
    plt.tight_layout()
