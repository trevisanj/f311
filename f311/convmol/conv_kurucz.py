"""
"""


import f311.physics as ph
import f311.filetypes as ft
from .. import convmol as cm
import a99
from .convlog import *
from collections import OrderedDict
import sys

__all__ = ["kurucz_to_sols"]



def kurucz_to_sols(mol_row, state_row, fileobj, qgbd_calculator, flag_hlf=False, flag_normhlf=False,
                   flag_fcf=False):
    """
    Converts Kurucz molecular lines data to PFANT "sets of lines"

    Args:
        mol_row: dict-like,
                 molecule-wide constants,
                 keys: same as as field names in 'moldb:molecule' table
        state_row: dict-like,
                   state-wide constants,
                   keys: same as field names in 'moldb:state' table
        fileobj: FileVald3 instance with only one species
        qgbd_calculator: callable that can calculate "qv", "gv", "bv", "dv",
                         e.g., calc_qbdg_tio_like()
        flag_hlf: Whether to calculate the gf's using Honl-London factors or
                  use Kurucz's loggf instead

        flag_normhlf: Whether to multiply calculated gf's by normalization factor


    Returns: (a list of ftpyfant.SetOfLines objects, a MolConversionLog object)
    """

    def append_error(msg):
        log.errors.append("#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), str(msg)))

    # C     BAND (v',v'')=(VL,V2L)
    # C     WN: vacuum wavenumber   WL : air wavelength
    # C     J2L: lower state angular momentum number
    # C     iso: isotope/ 26: 12C16O, 36: 13C16O, 27: 12C17O, 28: 12C18O
    # C     ramo: branch, for P: ID=1, for R: ID=2
    # C     name: file name/ coisovLv2L
    # C     HL: Honl-London factor
    # C     FR: oscillator strength

    if not isinstance(fileobj, ft.FileKuruczMolecule):
        raise TypeError("Invalid type for argument 'fileobj': {}".format(type(fileobj).__name__))

    lines = fileobj.lines
    n = len(lines)

    S = mol_row["s"]
    DELTAK = mol_row["cro"]
    fe = mol_row["fe"]

    # TODO of course this hard-wire needs change; now just a text for OH A2Sigma-X2Pi
    LAML = 0  # Sigma
    LAM2L = 1 # Pi

    if flag_hlf:
        formulas = ph.doublet.get_honllondon_formulas(LAML, LAM2L)
    sols = OrderedDict()  # one item per (vl, v2l) pair
    log = MolConversionLog(n)


    # This factor allows to reproduce the Hônl-London factors in `moleculagrade.dat` for OH blue,
    # first set-of-lines
    scale_factor = 730.485807466/2

    for i, line in enumerate(lines):
        assert isinstance(line, ft.KuruczMolLine)
        # TODO is it spin 2l?
        branch = ph.doublet.quanta_to_branch(line.Jl, line.J2l, line.spin2l)
        try:
            # TODO take this outta here, for now just to filter to match others
            fcf = cm.get_fcf_oh(line.vl, line.v2l)

            wl = line.lambda_

            # Normaliza = 1/((2.0*line.J2l+1)*(2.0*S+1)*(2.0-DELTAK))

            if flag_normhlf:
                # k = 2 / ((2.0*line.J2l+1)*(2.0*S+1)*(2.0-DELTAK))
                # k = 2 / ((2.0*line.J2l+1))
                k = 2/ ((2*S+1) * (2*line.J2l+1) * (2-DELTAK))
                # k = (2.0*line.J2l+1)
                # k = (2*S+1) * (2*line.J2l+1) * (2-DELTAK)
            else:
                k = 1

#            k *= fe

            if flag_hlf:
                hlf = formulas[branch](line.J2l)
                gf_pfant = hlf*k

            else:
                # Normaliza = scale_factor * k
                gf_pfant = k*10**line.loggf

            # # TODO ask BLB for references on these Franck-Condon Factors & try to generalize (these are for OH only I think)
            # x = line.J2l * (line.J2l + 1)
            # if branch[0] == "P":
            #     fcf = 3.651E-2 * (1 + 4.309E-6 * x + 1.86E-10 * (x ** 2)) ** 2
            # elif branch[0] == "Q":
            #     fcf = 3.674E-2 * (1 + 6.634E-6 * x + 1.34E-10 * (x ** 2)) ** 2
            # elif branch[0] == "R":
            #     fcf = 3.698E-2 * (1 + 1.101E-5 * x + 7.77E-11 * (x ** 2)) ** 2
            # else:
            #     raise RuntimeError("Shouldn't fall in here (branch ie neither P/Q/R)")

 #           fcf = 1.3201e-1

            if flag_fcf:
                fcf = cm.get_fcf_oh(line.vl, line.v2l)

                gf_pfant *= fcf

                # if branch[0] == "P":
                #     gf_pfant *= 3.651E-2 * (1 + 4.309E-6 * x + 1.86E-10 * (x ** 2)) ** 2
                # elif branch[0] == "Q":
                #     gf_pfant *= 3.674E-2 * (1 + 6.634E-6 * x + 1.34E-10 * (x ** 2)) ** 2
                # elif branch[0] == "R":
                #     gf_pfant *= 3.698E-2 * (1 + 1.101E-5 * x + 7.77E-11 * (x ** 2)) ** 2
                # else:
                #     raise RuntimeError("Shouldn't fall in here (branch ie neither P/Q/R)")

            J2l_pfant = line.J2l
        except Exception as e:
            # if isinstance(e, ZeroDivisionError):
            #     print("OOOOOOOOOOOOOOOOOOOOOO")
            #     print(str(line))
            #     sys.exit()

            msg = "#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), a99.str_exc(e))
            log.errors.append(msg)
            a99.get_python_logger().exception(msg)
            continue

        sol_key = "%3d%3d" % (line.vl, line.v2l)  # (v', v'') transition (v_sup, v_inf)
        if sol_key not in sols:
            qgbd = qgbd_calculator(state_row, line.v2l)
            qqv = qgbd["qv"]
            ggv = qgbd["gv"]
            bbv = qgbd["bv"]
            ddv = qgbd["dv"]
            sols[sol_key] = ft.SetOfLines(line.vl, line.v2l, qqv, ggv, bbv, ddv, 1.)

        sol = sols[sol_key]
        sol.append_line(wl, gf_pfant, J2l_pfant, branch)

    return (list(sols.values()), log)
