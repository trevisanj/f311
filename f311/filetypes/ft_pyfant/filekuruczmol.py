"""VALD3 atomic or molecular lines file"""


__all__ = ["KuruczMolLine", "FileKuruczMolecule"]

# from ..gear import *
import sys
import a99
from .. import DataFile
import io
import fortranformat as ff
import os


@a99.froze_it
class KuruczMolLine(a99.AttrsPart):
    attrs = ["lambda_", "loggf", "J2l", "E2l", "Jl", "El", "atomn0", "atomn1", "state2l", "v2l",
             "lambda_doubling2l", "spin2l", "statel", "vl", "lambda_doublingl", "spinl", "iso",]

    def __init__(self, lambda_=None, loggf=None, J2l=None, E2l=None, Jl=None, El=None, atomn0=None,
                 atomn1=None, state2l=None, v2l=None, lambda_doubling2l=None, spin2l=None,
                 statel=None, vl=None, lambda_doublingl=None, spinl=None, iso=None):
        a99.AttrsPart.__init__(self)
        # Wavelength in **Angstrom*** (although it is is stored in nm)
        self.lambda_ = lambda_
        self.loggf = loggf
        self.J2l = J2l
        self.E2l = E2l
        self.Jl = Jl
        self.El = El
        self.atomn0 = atomn0
        self.atomn1 = atomn1
        self.state2l = state2l
        self.v2l = v2l
        self.lambda_doubling2l = lambda_doubling2l
        self.spin2l = spin2l
        self.statel = statel
        self.vl = vl
        self.lambda_doublingl = lambda_doublingl
        self.spinl = spinl
        self.iso = iso

    def __repr__(self):
        return "{}({}, {}, {}, {}, {}, {}, {}, {}, '{}', {}, '{}', {}, '{}', {}, '{}', {}, {})".\
            format(self.__class__.__name__, self.lambda_,
            self.loggf, self.J2l, self.E2l, self.Jl, self.El, self.atomn0, self.atomn1,
            self.state2l, self.v2l, self.lambda_doubling2l, self.spin2l, self.statel, self.vl,
            self.lambda_doublingl, self.spinl, self.iso,)


class FileKuruczMolecule(DataFile):
    """
    Kurucz molecular lines file

    **Note** Kurucz file so far refers to one molecule only. Apparently one single system as well,
             although we will record the system information (A, X etc)

    **Note** Load only
    """

    attrs = ["num_lines"]

    @property
    def num_lines(self):
        return len(self)

    def __len__(self):
        return len(self.lines)

    def __init__(self):
        DataFile.__init__(self)

        # list of KuruczMolLine objects
        self.lines = []

    def __iter__(self):
        return iter(self.lines)


    def _do_load(self, filename):

        # **note** Kurucz puts always the "double-line" values before the "line" values
        #
        #   Wl(nm)   loggf   J"    E(cm-1)  J'   E(cm-1)   H
        #   |        |       |     |        |    |         |O
        #   |        |       |     |        |    |         || electronic state
        #   |        |       |     |        |    |         || |v"=00
        #   |        |       |     |        |    |         || || lambda-doubling component
        #   |        |       |     |        |    |         || || |spin
        #   |        |       |     |        |    |         || || ||
        #   204.5126 -7.917  2.5    83.925  2.5  48964.990 108X00f1   A07e1   16
        #   204.7561 -7.745  3.5   202.380  3.5  49025.320 108X00f1   A07e1   16
        #   204.9400 -7.883  5.5   543.596  6.5  49322.740 108X00e1   A07e1   16
        #   205.0076 -7.931  3.5   201.931  2.5  48964.990 108X00e1   A07e1   16
        #   205.0652 -7.621  4.5   355.915  4.5  49105.280 108X00f1   A07e1   16
        #   205.0652 -7.621  4.5   355.915  4.5  49105.280 108X00f1   A07e1   16
        # 1         11     18   23        33   38         49          61      69 1-based
        # 0         10     17   22        32   37         48          60      68 0-based (pythonic)
        #
        # FORMAT(F10.4.F7.3,F5.1,F10.3,F5.1,F11.3,I4,A1,I2,A1,I1,3X,A1,I2,A1,I1,3X,I2)
        # "
        # The code for the diatomic molecules is two 2-digit element numbers in
        # ascending order.  The labels consist of the electronic state, the vibrational
        # level, the lambda-doubling component, and the spin state.  Sometimes two
        # characters are required for the electronic state and the format becomes
        # ,A2,I2,A1,i1,2X,.  Negative energies are predicted or extrapolated"
        #
        # http://kurucz.harvard.edu/linelists/0linelists.readme

        filesize = os.path.getsize(filename)
        num_lines = int(filesize/70)

        with open(filename, "r") as h:
            self._do_load_h(h, filename, num_lines)

    def _do_load_h(self, h, filename, num_lines=0):
        # Thank you Kurucz
        fr = ff.FortranRecordReader(
            '(F10.4,F7.3,F5.1,F10.3,F5.1,F11.3,I2,I2,A1,I2,A1,I1,3X,A1,I2,A1,I1,3X,I2)')
        r = 0  # counts rows of file
        ii = 0
        try:
            self.lines = []
            while True:
                s = h.readline().strip("\n")
                if len(s) == 0:
                    break

                line = KuruczMolLine()
                # FortranFormat too slow
                # line.lambda_, line.loggf, line.J2l, line.E2l, line.Jl, line.El, line.atomn0, \
                # line.atomn1, line.state2l, line.v2l, line.lambda_doubling2l, line.spin2l, \
                # line.statel, line.vl, line.lambda_doublingl, line.spinl, line.iso = fr.read(s)

                #
                line.lambda_ = float(s[0:10])*10
                line.loggf = float(s[10:17])
                line.J2l = float(s[17:22])
                line.E2l = float(s[22:32])
                line.Jl = float(s[32:37])
                line.El = float(s[37:48])
                line.atomn0 = int(s[48:50])
                line.atomn1 = int(s[50:52])
                line.state2l = s[52:53]
                line.v2l = int(s[53:55])
                line.lambda_doubling2l = s[55:56]
                line.spin2l = int(s[56:57])
                line.statel = s[60:61]
                line.vl = int(s[61:63])
                line.lambda_doublingl = s[63:64]
                line.spinl = int(s[64:65])
                line.iso = s[69:71]
                self.lines.append(line)
                r += 1
                ii += 1
                if ii == 103:
                    a99.get_python_logger().info(
                        "Loading '{}': {}".format(filename, a99.format_progress(r, num_lines)))
                    ii = 0


        except Exception as e:
            # f = type(e)(("Error around %d%s row of file '%s'" %
            #              (r + 1, a99.ordinal_suffix(r + 1), filename)) + ": " + str(
            #     e)).with_traceback(sys.exc_info()[2])
            raise RuntimeError("Error around %d%s row of file '%s': \"%s\"" %
                               (r + 1, a99.ordinal_suffix(r + 1), filename, a99.str_exc(e))) from e


def _fake_file():
    """Returns StringIO for a fragment of a Kurucz molecular lines file"""

    f = io.StringIO()
    f.write("""  204.5126 -7.917  2.5    83.925  2.5  48964.990 108X00f1   A07e1   16
  204.7561 -7.745  3.5   202.380  3.5  49025.320 108X00f1   A07e1   16
  204.9400 -7.883  5.5   543.596  6.5  49322.740 108X00e1   A07e1   16
  205.0076 -7.931  3.5   201.931  2.5  48964.990 108X00e1   A07e1   16
  205.0652 -7.621  4.5   355.915  4.5  49105.280 108X00f1   A07e1   16
""")

    f.seek(0)
    return f


def _test():
    """Test code in docstring

    Example:

    >>> h = _fake_file()
    >>> f = FileKuruczMolecule()
    >>> f._do_load_h(h, "_fake_file")
    >>> f.lines[0]
    KuruczMolLine(2045.126, -7.917, 2.5, 83.925, 2.5, 48964.99, 1, 8, 'X', 0, 'f', 1, 'A', 7, 'e', 1, 6)
    """
    return

# h = _fake_file()
# f = FileVald3()
# f._do_load_h(h, "_fake_file")
