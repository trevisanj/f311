"""VALD3 atomic or molecular lines file"""


__all__ = ["KuruczMolLine", "KuruczMolLineOld", "KuruczMolLineOld1", "FileKuruczMolecule", "FileKuruczMoleculeOld",
           "FileKuruczMoleculeBase", "load_kurucz_mol", "FileKuruczMoleculeOld1", "FileKuruczMolecule1"]

# from ..gear import *
import sys
import a99
from .. import DataFile
import io
import fortranformat as ff
import os
from collections import namedtuple


# Will update progress status every time the following number of lines is read from file
_PROGRESS_INDICATOR_PERIOD = 1030 * 5


KuruczMolLine = namedtuple("KuruczMolLine",
    ["lambda_", "loggf", "J2l", "E2l", "Jl", "El", "atomn0", "atomn1", "state2l", "v2l",
    "lambda_doubling2l", "spin2l", "statel", "vl", "lambda_doublingl", "spinl", "iso", ])


KuruczMolLineOld = namedtuple("KuruczMolLineOld",
                              ["lambda_", "J2l", "Jl", "atomn0", "atomn1", "state2l", "v2l",
                               "lambda_doubling2l", "spin2l", "statel", "vl", "lambda_doublingl",
                               "spinl", ])

KuruczMolLineOld1 = namedtuple("KuruczMolLineOld1",
                              ["lambda_", "J2l", "Jl", "state2l", "v2l", "spin2l", "statel", "vl",
                               "spinl", ])


def load_kurucz_mol(filename):
    """
    Attempts to load Kurucz molecular line list (tries old and new format)

    Returns:
        FileKuruczMoleculeBase: either FileKuruczMolecule or FileKuruczMoleculeOld
    """
    from f311 import filetypes as ft
    return ft.load_with_classes(filename, [FileKuruczMolecule, FileKuruczMolecule1,
                                           FileKuruczMoleculeOld, FileKuruczMoleculeOld1,])


class FileKuruczMoleculeBase(DataFile):
    """Base class for the two types of Kurucz molecular lines file"""

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

    def __getitem__(self, item):
        return self.lines.__getitem__(item)


@a99.froze_it
class FileKuruczMolecule(FileKuruczMoleculeBase):
    """
    Kurucz molecular lines file

    **Note** Kurucz file so far refers to one molecule only.

    **Note** Load only
    """

    def _do_load(self, filename):

        # **note** Kurucz puts always the "double-line" values before the "line" values
        #
        #   Wl(nm)   loggf   J"    E(cm-1)  J'   E(cm-1)   H
        #   |        |       |     |        |    |         |O
        #   |        |       |     |        |    |         || electronic state
        #   |        |       |     |        |    |         || |v"=00
        #   |        |       |     |        |    |         || || lambda-doubling component
        #   |        |       |     |        |    |         || || |spin2l
        #   |        |       |     |        |    |         || || ||
        #
        #   204.5126 -7.917  2.5    83.925  2.5  48964.990 108X00f1   A07e1   16
        #   204.7561 -7.745  3.5   202.380  3.5  49025.320 108X00f1   A07e1   16
        #   204.9400 -7.883  5.5   543.596  6.5  49322.740 108X00e1   A07e1   16
        #   205.0076 -7.931  3.5   201.931  2.5  48964.990 108X00e1   A07e1   16
        #   205.0652 -7.621  4.5   355.915  4.5  49105.280 108X00f1   A07e1   16
        #   205.0652 -7.621  4.5   355.915  4.5  49105.280 108X00f1   A07e1   16
        # 1         11     18   23        33   38         49          61      69 1-based
        # 0         10     17   22        32   37         48          60      68 0-based
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
        r = 0  # counts rows of file
        ii = 0
        try:
            self.lines = []
            while True:
                s = h.readline().strip("\n")
                if len(s) == 0:
                    break

                # Kurucz: "negative energies are predicted or extrapolated"
                # (http: // kurucz.harvard.edu / linelists.html)
                E2l = float(s[22:32])
                if E2l < 0:
                    E2l = -E2l
                El = float(s[37:48])
                if El < 0:
                    El = -El

                try:
                    spin2l = int(s[56:57])
                except ValueError:
                    spin2l = 0

                try:
                    spinl = int(s[64:65])
                except ValueError:
                    spinl = 0

                line = KuruczMolLine(
                    float(s[0:10]) * 10,
                    float(s[10:17]),
                    float(s[17:22]),
                    E2l,
                    float(s[32:37]),
                    El,
                    int(s[48:50]),
                    int(s[50:52]),
                    s[52:53],
                    int(s[53:55]),
                    s[55:56],
                    spin2l,
                    s[60:61],
                    int(s[61:63]),
                    s[63:64],
                    spinl,
                    int(s[68:70]), )


                self.lines.append(line)
                r += 1
                ii += 1
                if ii == _PROGRESS_INDICATOR_PERIOD:
                    a99.get_python_logger().info(
                        "Loading '{}': {}".format(filename, a99.format_progress(r, num_lines)))
                    ii = 0


        except Exception as e:
            # f = type(e)(("Error around %d%s row of file '%s'" %
            #              (r + 1, a99.ordinal_suffix(r + 1), filename)) + ": " + str(
            #     e)).with_traceback(sys.exc_info()[2])
            raise RuntimeError("Error around %d%s row of file '%s': \"%s\"" %
                               (r + 1, a99.ordinal_suffix(r + 1), filename, a99.str_exc(e))) from e


@a99.froze_it
class FileKuruczMolecule1(FileKuruczMoleculeBase):
    """
    Kurucz molecular lines file following format of file "c2dabrookek.asc"
    """

    def _do_load(self, filename):

        # **note** Kurucz puts always the "double-line" values before the "line" values
        #
        #     Wl(nm) loggf    J"   E(cm-1)   J'    E(cm-1) C C
        #          |      |    |         |    |          | | |multiplicity
        #          |      |    |         |    |          | | ||electronic state
        #          |      |    |         |    |          | | |||v"=00
        #          |      |    |         |    |          | | |||| lambda-doubling component
        #          |      |    |         |    |          | | |||| |spin2l
        #          |      |    |         |    |          | | |||| ||
        #   287.7558-14.533 23.0  2354.082 24.0 -37095.578 6063a00e1  3d10e3  12 677  34741.495
        #   287.7564-14.955 22.0  2282.704 23.0 -37024.124 6063a00f1  3d10f3  12 677  34741.419
        #   287.7582-14.490 21.0  2214.696 22.0 -36955.900 6063a00e1  3d10e3  12 677  34741.205
        #   287.7613-15.004 24.0  2428.453 25.0 -37169.280 6063a00f1  3d10f3  12 677  34740.828
        #   287.7650-14.899 20.0  2149.765 21.0 -36890.147 6063a00f1  3d10f3  12 677  34740.382
        #   287.7671-14.573 25.0  2506.275 26.0 -37246.411 6063a00e1  3d10e3  12 677  34740.136
        #   287.7739-14.442 19.0  2088.132 20.0 -36827.442 6063a00e1  3d10e3  12 677  34739.310
        # 0         1         2         3         4         5         6         7         8
        # 012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
        #   205.0652 -7.621  4.5   355.915  4.5  49105.280 108X00f1   A07e1   16

        filesize = os.path.getsize(filename)
        num_lines = int(filesize/84)

        with open(filename, "r") as h:
            self._do_load_h(h, filename, num_lines)

    def _do_load_h(self, h, filename, num_lines=0):
        r = 0  # counts rows of file
        ii = 0
        try:
            self.lines = []
            while True:
                s = h.readline().strip("\n")
                if len(s) == 0:
                    break

                # Kurucz: "negative energies are predicted or extrapolated"
                # (http: // kurucz.harvard.edu / linelists.html)
                E2l = float(s[22:32])
                if E2l < 0:
                    E2l = -E2l
                El = float(s[37:48])
                if El < 0:
                    El = -El

                try:
                    spin2l = int(s[57:58])
                except ValueError:
                    spin2l = 0

                try:
                    spinl = int(s[65:66])
                except ValueError:
                    spinl = 0

                line = KuruczMolLine(
                    float(s[0:10]) * 10,
                    float(s[10:17]),
                    float(s[17:22]),
                    E2l,
                    float(s[32:37]),
                    El,
                    int(s[48:50]),
                    int(s[50:52]),
                    s[53:54],
                    int(s[54:56]),
                    s[56:57],
                    spin2l,
                    s[61:62],
                    int(s[62:64]),
                    s[64:65],
                    spinl,
                    int(s[68:70]), )


                self.lines.append(line)
                r += 1
                ii += 1
                if ii == _PROGRESS_INDICATOR_PERIOD:
                    a99.get_python_logger().info(
                        "Loading '{}': {}".format(filename, a99.format_progress(r, num_lines)))
                    ii = 0


        except Exception as e:
            # f = type(e)(("Error around %d%s row of file '%s'" %
            #              (r + 1, a99.ordinal_suffix(r + 1), filename)) + ": " + str(
            #     e)).with_traceback(sys.exc_info()[2])
            raise RuntimeError("Error around %d%s row of file '%s': \"%s\"" %
                               (r + 1, a99.ordinal_suffix(r + 1), filename, a99.str_exc(e))) from e





@a99.froze_it
class FileKuruczMoleculeOld(FileKuruczMoleculeBase):
    """
    Kurucz molecular lines file, old format #0

    This file format is Ssimilar to FileKuruczMol format, but contains less columns

    One example of file is: ATMOS/wrk4/bruno/Mole/CH/ch36.txt
    """

    def _do_load(self, filename):

        # **Note** The variable names below are the ones found in ATMOS/wrk4/bruno/Mole/CH/selech.f
        #
        #       lamb   j2   j1     v2l
        #          |    |    |      | d2l s1l
        #          |    |    |      | |   |
        #          |    |    |      | |   | v1l
        #          |    |    |      | |   | | d1l
        #          |    |    |      | |   | | |
        #   3001.028 16.5 17.5 106X02F2   C03F2
        # 0         1         2         3
        # 0123456789012345678901234567890123456


        filesize = os.path.getsize(filename)
        num_lines = int(filesize / 37)

        with open(filename, "r") as h:
            self._do_load_h(h, filename, num_lines)

    def _do_load_h(self, h, filename, num_lines=0):
        r = 0  # counts rows of file
        ii = 0
        try:
            self.lines = []
            while True:
                s = h.readline().strip("\n")
                if len(s) == 0:
                    break

                line = KuruczMolLineOld(
                    float(s[0:10]),
                    float(s[10:15]),
                    float(s[15:20]),
                    int(s[20:22]),
                    int(s[22:24]),
                    s[24:25],
                    int(s[25:27]),
                    s[27:28],
                    int(s[28:29]),
                    s[32:33],
                    int(s[33:35]),
                    s[35:36],
                    int(s[36:37]),
                )

                self.lines.append(line)
                r += 1
                ii += 1
                if ii == _PROGRESS_INDICATOR_PERIOD:
                    a99.get_python_logger().info(
                        "Loading '{}': {}".format(filename,
                                                  a99.format_progress(r, num_lines)))
                    ii = 0

        except Exception as e:
            raise RuntimeError("Error around %d%s row of file '%s': \"%s\"" %
                               (r + 1, a99.ordinal_suffix(r + 1), filename,
                                a99.str_exc(e))) from e


@a99.froze_it
class FileKuruczMoleculeOld1(FileKuruczMoleculeBase):
    """
    Kurucz molecular lines file, old format #1

    Not sure if this is really a Kurucz format. Found one file like this in:
    ATMOS/wrk4/bruno/Mole/CN/cnbx36.txt
    """

    def _do_load(self, filename):

        # **Note** The variable names below are the ones found in ATMOS/wrk4/bruno/Mole/CN/selecn.f
        #
        #      lamb   j2l   j1l v2l d2l
        #         |     |     |   | |   v1l
        #         |     |     |   | |   | d1l
        #         |     |     |   | |   | |
        #  3601.583 149.5 150.5 X00 2 B00 2

        # 0         1         2         3
        # 0123456789012345678901234567890123456


        filesize = os.path.getsize(filename)
        num_lines = int(filesize/33)

        with open(filename, "r") as h:
            self._do_load_h(h, filename, num_lines)

    def _do_load_h(self, h, filename, num_lines=0):
        r = 0  # counts rows of file
        ii = 0
        try:
            self.lines = []
            while True:
                s = h.readline().strip("\n")
                if len(s) == 0:
                    break


                """
                KuruczMolLineOld1 = namedtuple("KuruczMolLineOld1",
                              ["lambda_", "J2l", "Jl", "state2l", "v2l", "spin2l", "statel", "vl",
                               "spinl", ])

                """


                line = KuruczMolLineOld1(
                    float(s[0:9]),
                    float(s[9:15]),
                    float(s[15:21]),
                    s[22:23],
                    int(s[23:25]),
                    int(s[26:27]),
                    s[28:29],
                    int(s[29:31]),
                    int(s[32:33]),
                    )

                self.lines.append(line)
                r += 1
                ii += 1
                if ii == _PROGRESS_INDICATOR_PERIOD:
                    a99.get_python_logger().info(
                        "Loading '{}': {}".format(filename, a99.format_progress(r, num_lines)))
                    ii = 0

        except Exception as e:
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

