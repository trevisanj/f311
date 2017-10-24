"""Runs synthesis for molecular species separately. No atomic nor hydrogen lines."""

import f311.pyfant as pf
import f311.explorer as ex
import matplotlib.pyplot as plt
import f311.filetypes as ft
import a99

SUBPLOT_NUM_ROWS = 2
SUBPLOT_NUM_COLS = 2

if __name__ == "__main__":
    pf.copy_star(starname="sun-grevesse-1996")
    pf.link_to_data()

    # Loads full molecular lines file
    fmol = ft.FileMolecules()
    fmol.load()


    runnables = []
    for molecule in fmol:
        fmol2 = ft.FileMolecules()
        fmol2.molecules = [molecule]

        ecombo = pf.Combo()
        # Overrides file "molecules.dat" with in-memory object
        ecombo.conf.file_molecules = fmol2
        ecombo.conf.flag_output_to_dir = True
        oo = ecombo.conf.opt
        # Assigns synthesis range to match atomic lines range
        oo.llzero, oo.llfin = fmol2.llzero, fmol2.llfin
        # Turns off hydrogen lines
        oo.no_h = True
        # Turns off atomic lines
        oo.no_atoms = True
        # Adjusts the wavelength step according to the calculation interval
        oo.pas = max(1, round(oo.llfin*1./20000/2.5)*2.5)
        oo.aint = max(50., oo.pas)

        runnables.append(ecombo)

    pf.run_parallel(runnables)

    num_panels = SUBPLOT_NUM_COLS*SUBPLOT_NUM_ROWS
    num_molecules = len(runnables)
    ifigure = 0
    a99.format_BLB()
    for i in range(num_molecules+1):
        not_first = i > 0
        first_panel_of_figure = (i / num_panels - int(i / num_panels)) < 0.01
        is_panel = i < num_molecules

        if not_first and (not is_panel or first_panel_of_figure):
            plt.tight_layout()
            K = 1.
            a99.set_figure_size(plt.gcf(), 1500 * K, 740 * K)
            plt.tight_layout()
            filename_fig ="synthesis-molecules-{}.png".format(ifigure)
            print("Saving figure '{}'...".format(filename_fig))
            plt.savefig(filename_fig)
            plt.close()
            ifigure += 1

        if first_panel_of_figure and is_panel:
            plt.figure()

        if is_panel:
            ecombo = runnables[i]
            ecombo.load_result()

            isubplot = i % num_panels + 1
            plt.subplot(SUBPLOT_NUM_ROWS, SUBPLOT_NUM_COLS, isubplot)
            ex.draw_spectra_overlapped([ecombo.result["spec"]],
               setup=ex.PlotSpectrumSetup(flag_xlabel=i/3 >= 1, flag_legend=False))

            _title = fmol[i].description
            if "]" in _title:
                title = _title[:_title.index("]")+1]
            else:
                title = _title[:20]
            plt.title(title)
