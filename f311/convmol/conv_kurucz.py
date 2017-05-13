import f311.physics as ph
import f311.filetypes as ft
import a99
from .convlog import *
from collections import OrderedDict
from .conv import *

__all__ = ["ConvKurucz"]


class ConvKurucz(Conv):
    """Converts Kurucz molecular lines data to PFANT "sets of lines"

        Args:
            flag_hlf: Whether to calculate the gf's using Honl-London factors or
                      use Kurucz's loggf instead

                      ***Note** old format (FileKuruczMoleculeOld) does not have loggf information,
                                therefore the only way to work with the latter file type is
                                flag_hlf==True

            flag_normhlf: Whether to multiply calculated gf's by normalization factor

            flag_fcf: Whether to multiply calculated gf's by Franck-Condon Factor

            flag_quiet: Will not log exceptions when a molecular line fails

            flag_spinl: Whether or not to use the spinl of the Kurucz line list
                        for branch determination (spin2l is always used). Effect:

                - True: possible branches are P1, P12, P21, P2 and repeat for Q, R
                        (12 possibilities in total)

                - False: possible branches are P1, P2 and repeat for Q, R
                         (6 possibilities in total)

            iso: (int or None) isotope. If specified as int, only that isotope will be filtered;
                 otherwise, all isotopes in file will be included. Isotope is
                 field KuruczMolLine.iso (see KuruczMolLine, FileKuruczMol).

                 **Note** old Kurucz file format does not have the isotope information, therefore,
                          iso must be None or the thing will not work

    """

    def __init__(self, flag_hlf=False, flag_normhlf=False, flag_fcf=False, flag_quiet=False,
                 flag_spinl=False, fcfs=None, iso=None, *args, **kwargs):
        Conv.__init__(self, *args, **kwargs)
        self.flag_hlf = flag_hlf
        self.flag_normhlf = flag_normhlf
        self.flag_fcf = flag_fcf
        self.flag_quiet = flag_quiet
        self.flag_spinl = flag_spinl
        self.fcfs = fcfs
        self.iso = iso

    def _make_sols(self, lines):

        def append_error(msg):
            log.errors.append("#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), str(msg)))

        if not isinstance(lines, ft.FileKuruczMoleculeBase):
            raise TypeError("Invalid type for argument 'fileobj': {}".format(type(lines).__name__))
        assert self.flag_hlf or isinstance(lines, ft.FileKuruczMolecule), \
               "Old-format file does not contain loggf, must activate Hönl-London factors"

        lines = lines.lines
        n = len(lines)

        S = self.mol_consts["s"]
        DELTAK = self.mol_consts["cro"]
        FE = self.mol_consts["fe"]
        LAML = 0  #self.mol_consts["from_spdf"]
        LAM2L = 1  #self.mol_consts["to_spdf"]
        STATEL = self.mol_consts["from_label"]
        STATE2L = self.mol_consts["to_label"]

        if self.flag_hlf:
            formulas = ph.doublet.get_honllondon_formulas(LAML, LAM2L)
        sols = OrderedDict()  # one item per (vl, v2l) pair
        log = MolConversionLog(n)

        for i, line in enumerate(lines):
            if self.iso and line.iso != self.iso:
                log.skip_reasons["Isotope {}".format(line.iso)] += 1
                continue

            if line.statel != STATEL or line.state2l != STATE2L:
                log.skip_reasons["Transition {}-{}".format(line.statel, line.state2l)] += 1
                continue

            if self.flag_fcf:
                try:
                    fcf = self.fcfs[(line.vl, line.v2l)]
                except KeyError as e:
                    log.skip_reasons["FCF not available for (vl, v2l) = ({}, {})".format(line.vl, line.v2l)] += 1
                    continue

            branch = ph.doublet.quanta_to_branch(line.Jl, line.J2l,
                spinl=None if not self.flag_spinl else line.spinl, spin2l=line.spin2l)
            try:
                wl = line.lambda_

                if self.flag_normhlf:
                    # k = 2 / ((2.0*line.J2l+1)*(2.0*S+1)*(2.0-DELTAK))
                    # k = 2 / ((2.0*line.J2l+1))
                    k = 2./ ((2*S+1) * (2*line.J2l+1) * (2-DELTAK))
                    # k = (2.0*line.J2l+1)
                    # k = (2*S+1) * (2*line.J2l+1) * (2-DELTAK)
                else:
                    k = 1.

    #            k *= fe

                if self.flag_hlf:
                    try:
                        hlf = formulas[branch](line.J2l)
                    except ZeroDivisionError:
                        log.skip_reasons["Division by zero calculating HLF"] += 1
                        continue
                    gf_pfant = hlf*k

                else:
                    gf_pfant = k*10**line.loggf

                if self.flag_fcf:
                    gf_pfant *= fcf

                J2l_pfant = line.J2l
            except Exception as e:
                msg = "#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), a99.str_exc(e))
                log.errors.append(msg)
                if not self.flag_quiet:
                    a99.get_python_logger().exception(msg)
                continue

            sol_key = "%3d%3d" % (line.vl, line.v2l)  # (v', v'') transition (v_sup, v_inf)
            if sol_key not in sols:
                qgbd = self._calculate_qgbd(line.v2l)
                sols[sol_key] = ft.SetOfLines(line.vl, line.v2l,
                                              qgbd["qv"], qgbd["gv"], qgbd["bv"], qgbd["dv"], 1.)

            sol = sols[sol_key]
            sol.append_line(wl, gf_pfant, J2l_pfant, branch)

        return (list(sols.values()), log)
