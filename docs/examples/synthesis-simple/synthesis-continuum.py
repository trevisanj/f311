"""Runs synthesis over large wavelength range, then plots continuum"""

import f311.pyfant as pf
import f311.explorer as ex
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # Copies files main.dat and abonds.dat to local directory (for given star)
    pf.copy_star(starname="sun-grevesse-1996")
    # Creates symbolic links to all non-star-specific files, such as atomic & molecular lines,
    # partition functions, etc.
    pf.link_to_data()

    # Creates object that will run the four Fortran executables (innewmarcs, hydro2, pfant, nulbad)
    obj = pf.Combo()
    oo = obj.conf.opt
    # synthesis interval start (angstrom)
    oo.llzero = 2500
    # synthesis interval end (angstrom)
    oo.llfin = 30000
    # savelength step (angstrom)
    oo.pas = 1.
    # Turns off hydrogen lines
    oo.no_h = True
    # Turns off atomic lines
    oo.no_atoms = True
    # Turns off molecular lines
    oo.no_molecules = True

    obj.run()
    obj.load_result()
    print("obj.result = {}".format(obj.result))
    res = obj.result
    ex.draw_spectra([res["cont"]], setup=ex.PlotSpectrumSetup(fmt_ylabel=None))
    plt.savefig("continuum.png")
    plt.show()
