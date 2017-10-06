import f311.physics as ph
import f311.filetypes as ft
#from .. import convmol as cm
import a99
from .convlog import *
from collections import OrderedDict
import sys
import numpy as np
from .conv import *


__all__ = ["ConvPlez"]


# TODO This is incomplete: have to sort other things first. The main issue is whether we are going to extarct more than one system at once from one of these multiple-system files

class ConvPlez(Conv):
    """Converts Plez molecular lines data to PFANT "sets of lines" """

    def __init__(self, flag_hlf=False, flag_normhlf=False, flag_fcf=False, flag_quiet=False,
                 fcfs=None, *args, **kwargs):
        Conv.__init__(self, *args, **kwargs)
        self.flag_hlf = flag_hlf
        self.flag_normhlf = flag_normhlf
        self.flag_fcf = flag_fcf
        self.flag_quiet = flag_quiet
        self.fcfs = fcfs


    def _make_sols(self, lines):
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

        if not isinstance(self.lines, ft.FilePlezTiO):
            raise TypeError("Invalid type for argument 'lines': {}".format(type(lines).__name__))

        transition_dict = filemoldb.get_transition_dict()
        linedata = lines.get_numpy_array()

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
        #         molconsts = transition_dict[(molconsts["formula"], state_from, state_to)]
        #         tr["id_state"] = molconsts["id_state"]
        #     except KeyError as e:
        #         msg = "Will have to skip transition: '{}'".format(a99.str_exc(e))
        #         log.errors.append(msg)
        #         if not flag_quiet:
        #             a99.get_python_logger().exception(msg)
        #         continue



        sols = []

        S = molconsts.get_S2l()
        DELTAK = molconsts.get_deltak()
        fe = molconsts["fe"]

        # TODO of course this hard-wire needs change; now just a text for OH A2Sigma-X2Pi
        LAML = 0  # Sigma
        LAM2L = 1 # Pi

        if self.flag_hlf:
            formulas = ph.doublet.get_honllondon_formulas(LAML, LAM2L)
        log = MolConversionLog(len(lines))

        for tr in trset:
            state_from = tr["state_from"].decode("ascii")
            state_to = tr["state_to"].decode("ascii")
            try:
                molconsts = transition_dict[(molconsts["formula"], state_from, state_to)]
            except KeyError as e:
                msg = "Will have to skip transition: '{}'".format(a99.str_exc(e))
                log.errors.append(msg)
                if not self.flag_quiet:
                    a99.get_python_logger().exception(msg)
                continue

            qgbd = self.calculate_qgbd(tr["vlow"])
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
