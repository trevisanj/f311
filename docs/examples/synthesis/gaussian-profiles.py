"""
Nulbad's "impulse response"

Saves "impulse" spectrum (just a spike at lambda=5000 angstrom) as "flux.norm",
then runs `nulbad` repeatedly to get a range of Gaussian profiles.

"""

import f311.pyfant as pf
import f311.explorer as ex
import matplotlib.pyplot as plt
import a99
import f311.filetypes as ft
import numpy as np


# FWHM (full width at half of maximum) of Gaussian profiles in angstrom
FWHMS = [0.03, 0.06, 0.09, 0.12, 0.15, 0.20, 0.25, 0.3]

if __name__ == "__main__":
    # Copies files main.dat and abonds.dat to local directory (for given star)
    pf.copy_star(starname="sun-grevesse-1996")
    # Creates symbolic links to all non-star-specific files
    pf.link_to_data()

    # # 1) Creates "impulse" spectrum
    fsp = ft.FileSpectrumPfant()
    sp = ft.Spectrum()
    N = 2001
    sp.x = (np.arange(0, N, dtype=float)-(N-1)/2)*0.001+5000
    sp.y = np.zeros((N,), dtype=float)
    sp.y[int((N-1)/2)] = 1.

    fsp.spectrum = sp
    fsp.save_as("flux.norm")

    # # 2) Convolutions
    spectra = []
    for fwhm in FWHMS:
        enulbad = pf.Nulbad()
        enulbad.conf.opt.fwhm = fwhm
        enulbad.run()
        enulbad.load_result()
        enulbad.clean()
        # Appends convolved spectrum for comparison
        spectra.append(enulbad.result["convolved"])

    # # 3) Plots
    ex.draw_spectra_overlapped(spectra)
    K = 0.7
    a99.set_figure_size(plt.gcf(), 1300*K, 500*K)
    plt.tight_layout()
    plt.savefig("gaussian-profiles.png")
    plt.show()
