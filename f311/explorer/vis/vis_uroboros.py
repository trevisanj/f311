from ... import filetypes as ft
from .basic import Vis
import matplotlib.pyplot as plt
import a99
import numpy as np

__all__ = ["VisGalfitFig", "draw_galfit_tiles"]


# TODO setup image size

class VisGalfitFig(Vis):
    """Draw tiles: (INPUT, MODEL, RESIDUAL) x (bands)"""

    input_classes = (ft.FileGalfit,)
    action = __doc__

    def _do_use(self, m):
        draw_galfit_tiles(m)
        plt.show()


def draw_galfit_tiles(filegalfit, image_width=1000):
    """Draws a new matplotilb figure and returns it

    The figure will contain  = 3*(number of bands) subplots

    Args:
        filegalfit: FileGalfit instance
        image_width=1000: image width in pixels

    Returns:
        matplotlib figure
    """
    # TODO fine-tune axis positions (not with tight_layout())

    num_rows = len(filegalfit.kind_names)
    num_cols = len(filegalfit.band_names)
    fig, axarr = plt.subplots(num_rows+1, num_cols, squeeze=False)
    for i, kind_name in enumerate(filegalfit.kind_names):
        for j, band_name in enumerate(filegalfit.band_names):
            ax = axarr[i, j]
            hdu = filegalfit.get_frame(kind_name, band_name)

            remove_ticks(ax)

            im = hdu.data
            # Clips negative values
            im[im < 0] =  0

            # Transforms color values to something that will enhance small values
            image_data = np.power(im, 0.2)
            hei, wid = image_data.shape

            ax.imshow(image_data, cmap='gray')
            ax.set_ylim([0, hei - 1])
            ax.set_xlim([0, wid - 1])

            if i == 0:
                # First row, will indicate band on top
                ax.text(wid/2, hei+4, filegalfit.band_names[j],
                        horizontalalignment='center',
                        verticalalignment='bottom')
                # plt.title(filegalfit.band_names[i])

            if j == num_cols-1:
                # Last column, will write kind_name as rotated text at the right of the tile
                ax.text(wid+4, hei/2, filegalfit.kind_names[i],
                        horizontalalignment='left',
                        verticalalignment='center',
                        rotation=90)

    if True:
        for j, band_name in enumerate(filegalfit.band_names):
            ax = axarr[3, j]
            hdu = filegalfit.get_frame("MODEL", band_name)



            for x in ["top", "left", "right", "bottom"]:
                ax.spines[x].set_visible(False)
            # ax.set_box("off")
            remove_ticks(ax)

            im = hdu.data
            hei, wid = hdu.data.shape

            ax.set_ylim([0, hei - 1])
            ax.set_xlim([0, wid - 1])

            CHI2NU = "\n\nCHI2NU={:g}".format(hdu.header["CHI2NU"]) if j == 0 else ""
            RE = hdu.header["2_RE_{}".format(band_name.upper())]
            N = hdu.header["2_N_{}".format(band_name.upper())]
            RS = hdu.header["3_RS_{}".format(band_name.upper())]
            ax.text(2, hei - 1, "RE={}\nN={}\nRS={}{}".format(RE, N, RS, CHI2NU),
                    horizontalalignment='left',
                    verticalalignment='top', fontsize=7, color='red',
                    bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 2})

    a99.set_figure_size(fig, image_width, image_width/num_cols*4)
    plt.tight_layout()


def remove_ticks(ax):
    # http://stackoverflow.com/questions/12998430/remove-xticks-in-a-matplot-lib-plot
    ax.xaxis.set_major_locator(plt.NullLocator())
    ax.yaxis.set_major_locator(plt.NullLocator())

#
# class VisGalfitFig(Vis):
#     """Draw figure of 3 x 5 tiles"""
#
#     input_classes = (ft.FileGalfit,)
#     action = __doc__
#
#     def _do_use(self, m):
#         draw_15_tiles(m.hdulist)
#         plt.show()
#
#
# def draw_15_tiles(hdulist, image_width=1000):
#     """Draws a new matplotilb figure and returns it
#
#     The figure will contain 15 = 3*5 subplots
#
#     Args:
#         hdulist: object obtained using astropy.io.fits.open. This represents
#                  a FITS file containing 20 frames.
#                  Frames from 2nd to 16th will be used
#         image_width=1000: image width in pixels
#
#     Returns:!
#         matplotlib figure
#     """
#
#     band_names = "ugriz"
#     row_names = ["Image", "Model", "Residual"]
#
#     # TODO fine-tune axis positions (not with tight_layout())
#
#
#     fig = plt.figure()
#     for i, hdu in enumerate(hdulist[1:16]):
#         plt.subplot(3, 5, i + 1)  # 1 + i // 5, 1 + i % 5)
#
#         # http://stackoverflow.com/questions/12998430/remove-xticks-in-a-matplot-lib-plot
#         plt.gca().xaxis.set_major_locator(plt.NullLocator())
#         plt.gca().yaxis.set_major_locator(plt.NullLocator())
#
#         im = hdu.data
#         # Clips negative values
#         im[im < 0] =  0
#         # Transforms color values to something that will enhance small values
#         image_data = np.power(im, 0.2)
#         hei, wid = image_data.shape
#
#         plt.imshow(image_data, cmap='gray')
#         plt.ylim([0, hei - 1])
#         plt.xlim([0, wid - 1])
#
#         if i < 5:
#             # First row, will indicate band on top
#             plt.gca().text(wid/2, hei+4, band_names[i],
#                     horizontalalignment='center',
#                     verticalalignment='bottom')
#             # plt.title(band_names[i])
#         if i % 5 == 4:
#             # Last column, will
#             # plt.gca().yaxis.set_label_position("right")
#             # plt.ylabel(row_names[int(i/5)])
#             plt.gca().text(wid+4, hei/2, row_names[int(i/5)],
#                     horizontalalignment='left',
#                     verticalalignment='center',
#                     rotation=90)
#
#
#
#     a99.set_figure_size(fig, image_width, image_width/5*3)
#     plt.tight_layout()
