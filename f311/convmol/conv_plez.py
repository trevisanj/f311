"""
"""


import f311.physics as ph
import f311.filetypes as ft
#from .. import convmol as cm
import a99
from .convlog import *
from collections import OrderedDict
import sys
import numpy as np


__all__ = ["plez_to_sols"]



def plez_to_sols(mol_row, state_row, fileobj, qgbd_calculator, flag_hlf=False, flag_normhlf=False,
                   flag_fcf=False, flag_quiet=False, filemoldb=None):
    """
    Converts Plez molecular lines data to PFANT "sets of lines"

    **Note** state_row is ignored

    Args:
        mol_row: dict-like,
                 molecule-wide constants,
                 keys: same as as field names in 'moldb:molecule' table

        state_row: dict-like,
                   state-wide constants,
                   keys: same as field names in 'moldb:state' table

        fileobj: FilePlezTiO instance

        qgbd_calculator: callable that can calculate "qv", "gv", "bv", "dv",
                         e.g., calc_qbdg_tio_like()

        flag_hlf: Whether to calculate the gf's using Honl-London factors or
                  use Plez's gf instead

        flag_normhlf: Whether to multiply calculated gf's by normalization factor

        flag_quiet: Will not log exceptions when a molecular line fails

        filemoldb: FileMolDB instance


    Returns: (a list of ftpyfant.SetOfLines objects, a MolConversionLog object)

    If calculation of a line fails, will catch exception, add to MolConversion log (and log using
    get_python_logger() if flag_quiet is False)
    """
    from f311 import convmol as cm

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

    if not isinstance(fileobj, ft.FilePlezTiO):
        raise TypeError("Invalid type for argument 'fileobj': {}".format(type(fileobj).__name__))

    transition_dict = filemoldb.get_transition_dict()
    linedata = fileobj.get_numpy_array()

    trcols = linedata[["vup", "vlow", "state_from", "state_to"]]
    trset = np.unique(trcols)
    # trset = trcols.drop_duplicates()
    # trset["id_state"] = 0
    #
    #
    # for _, tr in trset.iterrows():
    #     state_from = tr["state_from"].decode("ascii")
    #     state_to = tr["state_to"].decode("ascii")
    #     try:
    #         state_row = transition_dict[(mol_row["formula"], state_from, state_to)]
    #         tr["id_state"] = state_row["id"]
    #     except KeyError as e:
    #         msg = "Will have to skip transition: '{}'".format(a99.str_exc(e))
    #         log.errors.append(msg)
    #         if not flag_quiet:
    #             a99.get_python_logger().exception(msg)
    #         continue



    sols = []

    S = mol_row["s"]
    DELTAK = mol_row["cro"]
    fe = mol_row["fe"]

    # TODO of course this hard-wire needs change; now just a text for OH A2Sigma-X2Pi
    LAML = 0  # Sigma
    LAM2L = 1 # Pi

    if flag_hlf:
        formulas = ph.doublet.get_honllondon_formulas(LAML, LAM2L)
    log = MolConversionLog(len(fileobj))

    for tr in trset:
        state_from = tr["state_from"].decode("ascii")
        state_to = tr["state_to"].decode("ascii")
        try:
            state_row = transition_dict[(mol_row["formula"], state_from, state_to)]
        except KeyError as e:
            msg = "Will have to skip transition: '{}'".format(a99.str_exc(e))
            log.errors.append(msg)
            if not flag_quiet:
                a99.get_python_logger().exception(msg)
            continue

        qgbd = qgbd_calculator(state_row, tr["vlow"])
        qqv = qgbd["qv"]
        ggv = qgbd["gv"]
        bbv = qgbd["bv"]
        ddv = qgbd["dv"]
        sol = ft.SetOfLines(tr["vup"], tr["vlow"], qqv, ggv, bbv, ddv, 1., state_from, state_to)
        sols.append(sol)

        mask = trcols == tr  # Boolean mask for linedata
        for i, line in enumerate(linedata[mask]):
            try:
                wl = line["lambda_"]
                J2l = line["Jlow"]
                branch = line["branch"].decode("ascii")
                gf = line["gf"]

                if flag_normhlf:
                    k = 2./ ((2*S+1) * (2*J2l+1) * (2-DELTAK))
                else:
                    k = 1.

                if flag_hlf:
                    raise NotImplementedError("Hönl-London factors not implemented for Plez molecular lines file conversion")

                    # hlf = formulas[branch](line.J2l)
                    # gf_pfant = hlf*k

                else:
                    gf_pfant = k*gf

                if flag_fcf:
                    raise RuntimeError("Franck-Condon factors not implemented for Plez molecular lines file conversion")

                    # fcf = cm.get_fcf_oh(line.vl, line.v2l)
                    # gf_pfant *= fcf

                sol.append_line(wl, gf_pfant, J2l, branch)


            except Exception as e:
                msg = "#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), a99.str_exc(e))
                log.errors.append(msg)
                if not flag_quiet:
                    a99.get_python_logger().exception(msg)
                continue


    return (sols, log)
