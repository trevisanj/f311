__all__ = ["FileMain"]

import a99
from .. import DataFile


NINE_HUNDRED = 900


@a99.froze_it
class FileMain(DataFile):
    """
    PFANT Main Stellar Configuration

    Imitates the logic of reader_main.f90::read_main().

    Attributes match reader_main.f90::main_* (minus the "main_" prefix)
    """

    default_filename = "main.dat"
    attrs = ["titrav", "pas", "fwhm", "ivtot", "vvt", "tolv",
             "teff", "glog", "asalog", "nhe", "ptdisk", "mu",
             "flprefix", "llzero", "llfin", "aint"]
    editors = ["mained.py", "x.py"]

    def __init__(self):
        DataFile.__init__(self)
        self.titrav = None
        self.ecrit = None
        self.pas = None
        self.echx = None
        self.echy = None
        self.fwhm = None
        self.ivtot = None
        self.vvt = None
        self.tolv = None
        self.teff = None
        self.glog = None
        self.asalog = None
        self.nhe = None
        self.inum = None
        self.ptdisk = None
        self.mu = None
        self.afstar = None
        self.xxcor = None
        self.flprefix = None
        self.llzero = None
        self.llfin = None
        self.aint = None
        self.filetohy = None

    def _do_load(self, filename):
        """Loads from file."""

        with open(filename, "r") as h:
            self.titrav = h.readline().strip()
            self.ecrit, self.pas, self.echx, self.echy, self.fwhm = a99.str_vector(h)

            vvt = float(h.readline())
            self.ivtot = 1
            if vvt <= NINE_HUNDRED:
                self.vvt = [vvt]
            else:
                _ivtot = int(h.readline())
                self.tolv = a99.float_vector(h)
                self.vvt = a99.float_vector(h)
                self.ivtot = len(self.vvt)

                if not (self.ivtot == len(self.tolv) == len(vvt)):
                    raise RuntimeError("ivtot must match len(tolv) must match len(vvt)")

            self.teff, self.glog, self.asalog, self.nhe, self.inum = a99.str_vector(h)
            self.ptdisk, self.mu = a99.str_vector(h)
            self.afstar = float(h.readline())
            self.xxcor = a99.float_vector(h)
            self.flprefix = h.readline().strip()
            self.llzero, self.llfin, self.aint = a99.float_vector(h)

            self.filetohy = []
            for s in h.readlines():
                s = s.strip()
                if len(s) > 0:
                    self.filetohy.append(s)

        # remaining conversions
        self.ecrit, self.ptdisk = list(map(a99.str2bool, (self.ecrit, self.ptdisk)))
        self.pas, self.echx, self.echy, self.fwhm, self.teff, self.glog, \
        self.asalog, self.nhe, self.mu = \
            list(map(float, (self.pas, self.echx, self.echy, self.fwhm, self.teff,
                             self.glog, self.asalog, self.nhe, self.mu)))
        self.inum = int(self.inum)

    def _do_save_as(self, filename):
        """Saves to file."""
        assert isinstance(self.vvt, list), "vvt must be list!"
        list2str = lambda l: " ".join([str(x) for x in l])
        with open(filename, "w") as h:
            a99.write_lf(h, "%s" % self.titrav)
            a99.write_lf(h, "%s %s %s %s %s" % (a99.bool2str(self.ecrit),
                                            self.pas, self.echx, self.echy, self.fwhm))
            a99.write_lf(h, "%s" % self.vvt[0])
            if self.vvt[0] > NINE_HUNDRED:
                a99.write_lf(h, "%s" % len(self.vvt))  # self.ivtot)
                a99.write_lf(h, list2str(self.tolv))
                a99.write_lf(h, list2str(self.vvt))

            a99.write_lf(h, list2str([self.teff, self.glog, self.asalog, self.nhe, self.inum]))
            a99.write_lf(h, list2str([a99.bool2str(self.ptdisk), self.mu]))
            a99.write_lf(h, str(self.afstar))
            a99.write_lf(h, list2str(self.xxcor))
            a99.write_lf(h, self.flprefix)
            a99.write_lf(h, list2str([self.llzero, self.llfin, self.aint]))
            for filetoh in self.filetohy:
                a99.write_lf(h, filetoh)
