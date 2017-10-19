"""Runs synthesis over short wavelength range, then plots normalized and convolved spectrum"""

import f311.pyfant as pf
import f311.explorer as ex
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # Copies files main.dat and abonds.dat to local directory (for given star)
    pf.copy_star(starname="sun-grevesse-1996")
    # Creates symbolic links to all non-star-specific files, such as atomic & molecular lines,
    # partition functions, etc.
    pf.link_to_data()

    # # First run
    # Creates object that will run the four Fortran executables (innewmarcs, hydro2, pfant, nulbad)
    obj = pf.Combo()
    # synthesis interval start (angstrom)
    obj.conf.opt.llzero = 6530
    # synthesis interval end (angstrom)
    obj.conf.opt.llfin = 6535

    # Runs Fortrans and hangs until done
    obj.run()

    # Loads result files into memory. obj.result is a dictionary containing elements ...
    obj.load_result()
    print("obj.result = {}".format(obj.result))
    res = obj.result
    ex.draw_spectra_overlapped([res["norm"], res["convolved"]])
    plt.savefig("norm-convolved.png")
    plt.show()
