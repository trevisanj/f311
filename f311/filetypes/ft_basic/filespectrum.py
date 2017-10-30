"""Classes FileSpectrum and descendants"""

__all__ = ["FileSpectrum", "FileSpectrumPfant",
           "FileSpectrumNulbad", "FileSpectrumXY", "FileSpectrumFits"]


from .spectrum import Spectrum
# import fortranformat as ff # TODO get rid of this because it is too slow
import struct
import logging
from .datafile import DataFile
from a99 import overwrite_fits, write_lf
from astropy.io import fits
import os
from astropy import units as u
import numpy as np


class FileSpectrum(DataFile):
    """Base class for all files representing a single 1D spectrum"""
    attrs = ['spectrum']
    editors = ["splisted.py"]

    def __init__(self):
        DataFile.__init__(self)
        self.spectrum = Spectrum()

    def load(self, filename=None):
        """Method was overriden to set spectrum.filename as well"""
        DataFile.load(self, filename)
        self.spectrum.filename = filename


class FileSpectrumPfant(FileSpectrum):
    """
    PFANT Spectrum (`pfant` output)

    This file alternates a "header" line where most of the information is
    repeated, and a "values" line, with the values of the flux
    corresponding to the lambda interval lzero-lfin
    """

    default_filename = "flux.norm"

    @property
    def l0(self):
        if self.spectrum is not None:
            if self.spectrum.x is not None:
                return self.spectrum.x[0]
        return None

    @property
    def lf(self):
        if self.spectrum is not None:
            if self.spectrum.x is not None:
                return self.spectrum.x[-1]
        return None

    @property
    def pas(self):
        if self.spectrum is not None:
            return self.spectrum.delta_lambda
        return None

    def __init__(self):
        FileSpectrum.__init__(self)

        self.tit = ""
        self.tetaef = 0.
        self.glog = 0.
        self.asalog = 0.
        self.modeles_nhe = 0.
        self.amg = 0.
        self.echx = 0.
        self.echy = 0.
        self.fwhm = 0.

    def _do_load(self, filename):
#    55                            1.17895        1.55000       -0.54000        0.08511        0.00000    3083.0    3630.0    3083.0    3093.0      2001        0.00500        5.00000        1.00000        0.12000
# 12345                    123456789012345               123456789012345               123456789012345          1234567890          1234567890          123456789012345               123456789012345
#      12345678901234567890               123456789012345               123456789012345               1234567890          1234567890          1234567890               123456789012345               123456789012345
# ikeytot                                                                                             l0                                                pas
# 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
# 0         10        20        30        40        50        60        70        80        90        100       110       120       130       140       150

        with open(filename, 'r') as h:
            # f_header = ff.FortranRecordReader(
            #     "(i5, a20, 5f15.5, 4f10.1, i10, 4f15.5)")
            i = 0
            y = []
            sp = self.spectrum = Spectrum()

            while True:
                s = h.readline()
                if i == 0:
                    ikeytot = int(s[0:5])
                    l0 = float(s[100:110])
                    pas = float(s[150:165])

                    # vars_ = f_header.read(s)  # This is actually quite slow, gotta avoid it
                    # [ikeytot,
                    #  _,
                    #  _,
                    #  _,
                    #  _,
                    #  _,
                    #  _,
                    #  l0,
                    #  _,
                    #  _,  # lzero,
                    #  _,  # lfin,
                    #  _,  # itot
                    #  pas,
                    #  _,
                    #  _,
                    #  _] = vars_
                    #
                    # # [self.ikeytot,
                    # #  self.tit,
                    # #  self.tetaef,
                    # #  self.glog,
                    # #  self.asalog,
                    # #  self.modeles_nhe,
                    # #  self.amg,
                    # #  self.l0,
                    # #  self.lf,
                    # #  _,  # lzero,
                    # #  _,  # lfin,
                    # #  _,  # itot
                    # #  self.pas,
                    # #  self.echx,
                    # #  self.echy,
                    # #  self.fwhm] = vars_

                #itot = vars[11]

                # if False:
                # # Will have to compile a different formatter depending on itot
                #     if i == 0 or itot != last_itot:
                #       f_flux = ff.FortranRecordReader("(%df15.5)" % itot)
                #
                #     v = f_flux.read(h.readline())
                # else:
                # Will see if can read faster than Fortran formatter
                s = h.readline()

                # Note: last character of s is "\n"
                v = [float(s[0 + j:15 + j]) for j in range(0, len(s) - 1, 15)]

                # print len(v)
                # print "==========================="
                # print v
                # print i, self.ikeytot

                # if i < self.ikeytot - 1:
                if i < ikeytot - 1:
                    # Last point is discarded because pfant writes reduntantly:
                    # last point of iteration ikey is the same as first point of
                    # iteration ikey+1
                    # y = y + v  # update: taking all points calculated yes [:-1]
                    y = y + v[:-1]
                else:
                    # ...except for in the last calculation interval
                    # (then the last point is used).
                    y = y + v
                    break

                i += 1

                #last_itot = itot

        # Lambdas

        # sp.x = np.array([self.l0 + k * self.pas for k in range(0, len(y))])

        sp.x = np.array([l0 + k * pas for k in range(0, len(y))])

        sp.y = np.array(y)

#        logging.debug("Just read PFANT Spectrum '%s'" % filename)

    def _do_save_as(self, filename):
#    55                            1.17895        1.55000       -0.54000        0.08511        0.00000    3083.0    3630.0    3083.0    3093.0      2001        0.00500        5.00000        1.00000        0.12000
# 12345                    123456789012345               123456789012345               123456789012345          1234567890          1234567890          123456789012345               123456789012345
#      12345678901234567890               123456789012345               123456789012345               1234567890          1234567890          1234567890               123456789012345               123456789012345
# ikeytot                                                                                             l0                                                pas
# 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
# 0         10        20        30        40        50        60        70        80        90        100       110       120       130       140       150

        with open(filename, 'w') as h:


            fmt = "{:5d}{:20s}" \
                  "{:15.5f}{:15.5f}{:15.5f}{:15.5f}{:15.5f}" \
                  "{:10.1f}{:10.1f}{:10.1f}{:10.1f}" \
                  "{:10d}" \
                  "{:15.5f}{:15.5f}{:15.5f}{:15.5f}\n"

            ikeytot = 1
            itot = len(self.spectrum.y)

            h.write(fmt.format(
                ikeytot,
                self.tit,
                self.tetaef,
                self.glog,
                self.asalog,
                self.modeles_nhe,
                self.amg,
                self.l0,
                self.lf,
                self.l0,
                self.lf,
                itot,
                self.pas,
                self.echx,
                self.echy,
                self.fwhm
            ))

            h.write("".join(["{:15.5f}".format(a) for a in self.spectrum.y])+"\n")


class FileSpectrumNulbad(FileSpectrum):
    """
    PFANT Spectrum (`nulbad` output)

    This file is a two-column text file with two lines of comment at the beginning
    """

    def _do_load(self, filename):
        x = []
        y = []
        with open(filename, 'r') as h:
            sp = self.spectrum = Spectrum()
            # -- row 01 --
            # Original format: ('#',A,'Tef=',F6.3,X,'log g=',F4.1,X,'[M/H]=',F5.2,X,F5.2)
            # s_header0 = struct.Struct("1x 20s 4x 6s 7x 4s 7x 5s 1x 5s")
            s = h.readline()

            if not s.startswith("#"):
                raise RuntimeError("Not a nulbad output file")

            # [sp.tit, sp.tetaef, sp.glog, sp.asalog, sp.amg] = \
            #     s_header0.unpack_from(s)
            # [sp.tetaef, sp.glog, sp.asalog, sp.amg] = \
            #     list(map(float, [sp.tetaef, sp.glog, sp.asalog, sp.amg]))

            # -- row 02 --
            # Original format: ('#',I6,2X,'0. 0. 1. 1. Lzero =',F10.2,2x,'Lfin =', &
            # F10.2,2X,'PAS =',F5.2,2x,'FWHM =',F5.2)
            # s_header1 = struct.Struct("1x 6s 21x 10s 8x 10s 7x 5s 8x 5s")
            s = h.readline()

            if not s.startswith("#"):
                raise RuntimeError("Not a nulbad output file")

            # [_, sp.l0, sp.lf, sp.pas, sp.fwhm] = \
            #     s_header1.unpack_from(s)
            # [sp.l0, sp.lf, sp.pas, sp.fwhm] = \
            #     list(map(float, [sp.l0, sp.lf, sp.pas, sp.fwhm]))
            #n = int(n)


            # -- rows 03 ... --
            #
            # Examples:
            #    4790.0000000000000       0.99463000000000001
            #    4790.0400000000000        2.0321771294932130E-004

            # pattern = re.compile(r"^\s+([0-9.E+-]+)\s+([0-9.E+-]+)")
            while True:
                s = h.readline().strip()
                if not s:
                  break

                a, b = [float(z) for z in s.split()]
                # if match is None:
                #     raise ParseError('Row %d of file %s is invalid' % (i + 3, filename))
                # a, b = map(float, match.groups())

                x.append(a)
                y.append(b)

        sp.x = np.array(x)
        sp.y = np.array(y)

#        logging.debug("Just read NULBAD Spectrum '%s'" % filename)


class FileSpectrumXY(FileSpectrum):
    """
    "Lambda-flux" Spectrum (2-column text file)

    File may have comment lines; these will be ignored altogether, because the file
    is read with numpy.loadtxt()
    """

    def _do_load(self, filename):
        A = np.loadtxt(filename)
        if len(A.shape) < 2:
            raise RuntimeError("File {0!s} does not contain 2D array".format(filename))
        if A.shape[1] < 2:
            raise RuntimeError("File {0!s} must contain at least two columns".format(filename))
        if A.shape[1] > 2:
            logging.warning("File {0!s} has more than two columns, taking only first and second".format(filename))
        sp = self.spectrum = Spectrum()
        sp.x = A[:, 0]
        sp.y = A[:, 1]
#        logging.debug("Just read XY Spectrum '%s'" % filename)


    def _do_save_as(self, filename):
        with open(filename, "w") as h:
            for x, y in zip(self.spectrum.x, self.spectrum.y):
                write_lf(h, "{0:.10g} {1:.10g}".format(x, y))


class FileSpectrumFits(FileSpectrum):
    """FITS Spectrum"""
    flag_txt = False

    def _do_load(self, filename):
        fits_obj = fits.open(filename)
        # fits_obj.info()
        hdu = fits_obj[0]
        hdu.verify()
        sp = self.spectrum = Spectrum()
        sp.from_hdu(hdu)

    def _do_save_as(self, filename):
        """Saves spectrum back to FITS file."""

        if len(self.spectrum.x) < 2:
            raise RuntimeError("Spectrum must have at least two points")
        if os.path.isfile(filename):
            os.unlink(filename)  # PyFITS does not overwrite file

        hdu = self.spectrum.to_hdu()
        overwrite_fits(hdu, filename)
