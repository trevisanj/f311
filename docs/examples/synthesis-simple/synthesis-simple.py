import f311.pyfant as pf
import f311.explorer as ex

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
    ex.plot_spectra_overlapped([res["norm"], res["convolved"]])



    # # Another run, this time to plot the continuum over a large wavelength range
    obj = pf.Combo()
    oo = obj.conf.opt
    oo.llzero = 2500
    oo.llfin = 30000
    # Raises the wavelength step, otherwise will take minutes
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
    ex.plot_spectra([res["cont"]])
