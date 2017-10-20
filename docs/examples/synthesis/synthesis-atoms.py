"""Runs synthesis for specified atomic species separately. No molecules or hydrogen lines."""

import f311.pyfant as pf
import f311.explorer as ex
import matplotlib.pyplot as plt
import f311.filetypes as ft
import a99

# ["<element name><ionization level>", ...]
MY_SPECIES = ["Fe1", "Fe2", "Ca1", "Ca2", "Na1", "Si1"]

if __name__ == "__main__":
    pf.copy_star(starname="sun-grevesse-1996")
    pf.link_to_data()

    # Loads full atomic lines file
    fatoms = ft.FileAtoms()
    fatoms.load()


    runnables = []
    for elem_ioni in MY_SPECIES:
        atom = fatoms.find_atom(elem_ioni)

        # Creates atomic lines file object containing only one atom
        fatoms2 = ft.FileAtoms()
        fatoms2.atoms = [atom]

        ecombo = pf.Combo()
        # Overrides file "atoms.dat" with in-memory object
        ecombo.conf.file_atoms = fatoms2
        ecombo.conf.flag_output_to_dir = True
        oo = ecombo.conf.opt
        # Assigns synthesis range to match atomic lines range
        oo.llzero, oo.llfin = fatoms2.llzero, fatoms2.llfin
        # Turns off hydrogen lines
        oo.no_h = True
        # Turns off molecular lines
        oo.no_molecules = True

        runnables.append(ecombo)

    pf.run_parallel(runnables)

    # Draws figure
    f = plt.figure()
    a99.format_BLB()
    for i, (title, ecombo) in enumerate(zip(MY_SPECIES, runnables)):
        ecombo.load_result()
        plt.subplot(2, 3, i+1)
        ex.draw_spectra_overlapped([ecombo.result["spec"]],
                                   setup=ex.PlotSpectrumSetup(flag_xlabel=i/3 >= 1, flag_legend=False))
        plt.title(title)

    K = 1.
    a99.set_figure_size(plt.gcf(), 1300*K, 740*K)
    plt.tight_layout()
    plt.savefig("synthesis-atoms.png")
    plt.show()
