"""
Difference in continuum with/without opacities
"""

from pyfant import *
import sys

LLZERO = 3000
LLFIN = 16000

to_run = []

pf = Pfant()
pf.conf.opt.flprefix = "flux-absoru"
pf.conf.opt.opa = False
pf.conf.opt.absoru = True
pf.conf.opt.no_molecules = True
pf.conf.opt.no_atoms = True
pf.conf.opt.no_h = True
pf.conf.opt.llzero = LLZERO
pf.conf.opt.llfin = LLFIN
pf.conf.opt.pas = 1
to_run.append(pf)
inn = Innewmarcs()
inn.conf.opt = pf.conf.opt
inn.run()  # Creates modeles.mod

pf = Pfant()
pf.conf.opt.flprefix = "flux-opa"
pf.conf.opt.opa = True
pf.conf.opt.absoru = False
pf.conf.opt.no_molecules = True
pf.conf.opt.no_atoms = True
pf.conf.opt.no_h = True
pf.conf.opt.llzero = LLZERO
pf.conf.opt.llfin = LLFIN
pf.conf.opt.pas = 1
to_run.append(pf)
inn = Innewmarcs()
inn.conf.opt = pf.conf.opt
inn.run()  # Creates modeles.opa

manager = run_parallel(to_run, flag_console=False)

if not manager.flag_success:
    print("Not all pfant's succeeded running, so not plotting.")
    sys.exit()

# Loads continuum's and plots
spectra = []
for pf in to_run:
    assert isinstance(pf, Pfant)
    pf.load_result()
    pf.conf.sid.clean()
    spectra.append(pf.cont)

plot_spectra_overlapped(spectra, ymin=0)