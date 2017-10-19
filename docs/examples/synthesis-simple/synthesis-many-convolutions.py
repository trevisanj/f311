#!/usr/bin/env python

"""Runs synthesis over short wavelength range, then plots normalized and convolved spectrum"""

import f311.pyfant as pf
import f311.explorer as ex
import matplotlib.pyplot as plt
import a99

# FWHM (full width at half of maximum) of Gaussian profiles in angstrom
FWHMS = [0.03, 0.06, 0.09, 0.12, 0.15, 0.20, 0.25, 0.3, 0.5]

if __name__ == "__main__":
    # Copies files main.dat and abonds.dat to local directory (for given star)
    pf.copy_star(starname="sun-grevesse-1996")
    # Creates symbolic links to all non-star-specific files
    pf.link_to_data()

    # # 1) Spectral synthesis
    # Creates object that will run the four Fortran executables (innewmarcs, hydro2, pfant, nulbad)
    ecombo = pf.Combo()
    # synthesis interval start (angstrom)
    ecombo.conf.opt.llzero = 6530
    # synthesis interval end (angstrom)
    ecombo.conf.opt.llfin = 6535
    # Runs Fortrans and hangs until done
    ecombo.run()
    ecombo.load_result()
    # Retains un-convolved spectrum for comparison
    spectra = [ecombo.result["norm"]]

    # # 2) Convolutions
    for fwhm in FWHMS:
        enulbad = pf.Nulbad()
        enulbad.conf.opt.fwhm = fwhm
        enulbad.run()
        enulbad.load_result()
        # Appends convolved spectrum for comparison
        spectra.append(enulbad.result["convolved"])

    # # 3) Plots
    ex.draw_spectra_overlapped(spectra)
    K = 1.1
    a99.set_figure_size(plt.gcf(), 1000*K, 500*K)
    plt.tight_layout()
    plt.savefig("many-convs.png")
    plt.show()
