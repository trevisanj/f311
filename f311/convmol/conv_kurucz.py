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

    def __init__(self, flag_hlf=False, flag_fcf=False, flag_quiet=False, flag_special_fcf=False,
                 flag_spinl=False, fcfs=None, iso=None, *args, **kwargs):
        Conv.__init__(self, *args, **kwargs)
        self.flag_hlf = flag_hlf
        self.flag_fcf = flag_fcf
        self.flag_quiet = flag_quiet
        self.flag_spinl = flag_spinl
        self.flag_special_fcf = flag_special_fcf
        self.fcfs = fcfs
        self.iso = iso

    # TODO looks like this routine is kindda generic
    # TODO could dismember this later
    def _make_sols(self, lines):

        def append_error(msg):
            log.errors.append("#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), str(msg)))

        if not isinstance(lines, ft.FileKuruczMoleculeBase):
            raise TypeError("Invalid type for argument 'fileobj': {}".format(type(lines).__name__))
        assert self.flag_hlf or isinstance(lines, ft.FileKuruczMolecule), \
               "Old-format file does not contain loggf, must activate Hönl-London factors"

        lines = lines.lines
        n = len(lines)

        STATEL = self.molconsts["from_label"]
        STATE2L = self.molconsts["to_label"]

        mtools = self.multiplicity_toolbox()

        # Prepares result
        sols = ConvSols(self.qgbd_calculator, self.molconsts)
        log = MolConversionLog(n)

        for i, line in enumerate(lines):
            if self.iso and line.iso != self.iso:
                log.skip_reasons["Isotope {}".format(line.iso)] += 1
                continue

            if line.statel != STATEL or line.state2l != STATE2L:
                log.skip_reasons["Transition {}-{}".format(line.statel, line.state2l)] += 1
                continue


            branch = mtools.quanta_to_branch(line.Jl, line.J2l,
                spinl=(None if not self.flag_spinl else line.spinl), spin2l=line.spin2l)


            # This was only a test, but filters like these may be useful if line.spin2l != line.spinl:
            #     log.skip_reasons["Different spin"] += 1
            #     continue


            try:
                sj = 1.

                if self.flag_hlf:
                    try:
                        hlf = mtools.get_sj(line.vl, line.v2l, line.J2l, branch)
                    except ph.NoLineStrength:
                        log.skip_reasons["Cannot calculate HLF"] += 1
                        continue

                    if hlf < 0:
                        log.skip_reasons["Negative SJ"] += 1
                        continue

                    sj *= hlf

                else:
                    sj *= 10**line.loggf

                if self.flag_fcf:
                    sj *= self._get_fcf(line.vl, line.v2l, self.flag_special_fcf)

            except Exception as e:
                reason = a99.str_exc(e)
                log.skip_reasons[reason] += 1
                msg = "#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), reason)
                log.errors.append(msg)
                if not self.flag_quiet:
                    a99.get_python_logger().exception(msg)
                continue

            sols.append_line(line, sj, branch)

            # sol_key = "%3d%3d" % (line.vl, line.v2l)  # (v', v'') transition (v_sup, v_inf)
            # raise RuntimeError("Como que o calculate_qgbd esta fazendo, sendo que o dicionario molconsts agora tem prefixos to e from?")
            # if sol_key not in sols:
            #     qgbd = self._calculate_qgbd(line.v2l)
            #     sols[sol_key] = ft.SetOfLines(line.vl, line.v2l,
            #                                   qgbd["qv"], qgbd["gv"], qgbd["bv"], qgbd["dv"], 1.)
            #
            # sol = sols[sol_key]
            # sol.append_line(wl, gf_pfant, J2l_pfant, branch)

        return sols, log
