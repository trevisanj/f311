"""Visualization classes for pyfant file types"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D  # yes, required (see below)
import a99
import f311.filetypes as ft
from ..basic import Vis

class VisFileToH(Vis):
    """
    Plots hydrogen lines: each atmospheric layer is plotted as a y-axis-dislocated
    Spectrum in a 3D plot.
    """

    input_classes = (ft.FileToH,)
    action = "Visualize hydrogen lines profiles"

    def _do_use(self, r):
        fig = plt.figure()
        mpl.rcParams['legend.fontsize'] = 10
        fig.canvas.set_window_title(self.title)  # requires the Axes3D module
        ax = fig.gca(projection='3d')
        x = np.concatenate((2 * r.lambdh[0] - r.lambdh[-2::-1], r.lambdh))
        _y = np.ones(len(x))
        for i in range(r.th.shape[1]):
            z = np.concatenate((r.th[-2::-1, i], r.th[:, i]))
            # ax.plot(x, _y * (i + 1), np.log10(z), label='a', color='k')
            ax.plot(x, _y * (i + 1), z, label='a', color='k')
        ax.set_xlabel('Wavelength ($\AA$)')
        ax.set_ylabel("Atmospheric layer #")
        # ax.set_zlabel('log10(Intensity)')
        # ax.set_zlabel('?')
        plt.tight_layout()
        plt.show()


# # Editors

class VisAtoms(Vis):
    """Opens the ated window."""
    input_classes = (ft.FileAtoms,)
    action = "Edit using atomic lines editor"

    def _do_use(self, r):
        from f311 import explorer as ex
        form = a99.keep_ref(ex.XFileAtoms(self.parent_form))
        form.load(r)
        form.show()


class VisMolecules(Vis):
    """Opens the mled window."""
    input_classes = (ft.FileMolecules,)
    action = "Edit using molecular lines editor"

    def _do_use(self, r):
        from f311 import explorer as ex
        form = a99.keep_ref(ex.XFileMolecules(self.parent_form))
        form.load(r)
        form.show()


class VisMain(Vis):
    """Opens the mained window."""
    input_classes = (ft.FileMain,)
    action = "Edit using main configuration file editor"

    def _do_use(self, r):
        from f311 import explorer as ex
        form = a99.keep_ref(ex.XFileMain(self.parent_form, r))
        form.show()


class VisAbonds(Vis):
    """Opens the abed window."""
    input_classes = (ft.FileAbonds,)
    action = "Edit using abundances file editor"

    def _do_use(self, r):
        from f311 import explorer as ex
        form = a99.keep_ref(ex.XFileAbonds(self.parent_form, r))
        form.show()
