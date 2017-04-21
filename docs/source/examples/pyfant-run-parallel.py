"""
Runs combo for separate molecules

Put options.py in local directory for custom ForTran binary command-line options
"""


import f311.filetypes as ft
import f311.pyfant as pf
from collections import Counter
import os

FN_OBS = "obsmul-warped.fits"

def get_combo():
    c = pf.Combo(["pfant", "nulbad"])

    if os.path.isfile(ft.FileOptions.default_filename):
        opt = ft.FileOptions()
        opt.load()
        c.conf.opt = opt

    c.conf.opt.no_h = True
    c.conf.opt.no_atoms = True
    c.conf.opt.allow = True
    c.conf.opt.fwhm = 0.14
    return c

if __name__ == "__main__":
    print("loading '{}'...".format(FN_OBS))
    sp = ft.load_spectrum(FN_OBS)
    sp_lam_min = min(sp.wavelength)
    sp_lam_max = max(sp.wavelength)

    c = get_combo()

    f = ft.FileMolecules()
    f.load(c.conf.opt.fn_molecules)
    formulas = Counter()

    jobs = []
    for molecule in f:
        llzero = max(sp_lam_min, min(molecule.lmbdam))
        llfin = min(sp_lam_max, max(molecule.lmbdam))

        if llzero >= llfin:
            print("Molecule {} - {} skipped because of wavelength range being out of that of observed spectrum".
                  format(molecule.formula, molecule.description))

        f1 = ft.FileMolecules()
        f1.molecules.append(molecule)

        c = get_combo()
        c.conf.opt.flprefix = "{}-{:1d}".format(molecule.formula, formulas[molecule.formula])
        formulas[molecule.formula] += 1
        c.conf.opt.llzero = llzero
        c.conf.opt.llfin = llfin

        jobs.append(c)

    pf.run_parallel(jobs, flag_console=True)

