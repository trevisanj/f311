__all__ = [
"create_spectrum_lists", "load_bulk", "BulkItem", "load_eso_sky"]


import os.path
from collections import OrderedDict
import glob
import os
import re
import numpy as np
import a99
import f311.filetypes as ft
from astropy.io import fits
import astropy.units as u
import f311.explorer as ex
# from .. import aosss as ao


FILE_MAP = OrderedDict((
 ("cube_hr", ft.FileFullCube),
 ("cube_seeing", ft.FileFits),
 ("ifu_noseeing", ft.FileFullCube),
 ("mask_fiber_in_aperture", ft.FileFits),  # TODO, handle this file because it is nice
 ("reduced", ft.FileFullCube),
 ("reduced_snr", ft.FileFullCube),
 ("sky", ft.FileSpectrumFits),
 ("skysub", ft.FileSpectrumFits),
 ("spintg", ft.FileSpectrumFits),
 ("spintg_noseeing", "messed"),  # particular case
 ("therm", "messed"),            # particular case
))
#
# FILE_KEYWORDS = FILE_MAP.keys()


class BulkItem(object):
    """This is each item returned by load_bulk"""
    def __init__(self, keyword=None, fileobj=None, filename=None, flag_exists=None,
                 flag_supported=None, error=None):
        # fileobj may be a DataFile or a string (the latter if the .par file)
        self.keyword = keyword
        self.fileobj = fileobj
        self.filename = filename
        self.flag_exists = flag_exists
        self.flag_supported = flag_supported
        self.error = error


def load_bulk(simid, dir_='.'):
    """
    Loads all files given the simulation id. Returns an list of BulkItem

    The keys are the same as in FILE_KEYWORDS, in the same order as well
    """

    ret = []
    sp_ref = None  # reference spectrum for x-axis of messed files
    for keyword, class_ in list(FILE_MAP.items()):
        fn = os.path.join(dir_, "%s_%s.fits" % (simid, keyword))

        flag_exists = os.path.isfile(fn)
        flag_supported = class_ is not None
        error = None
        fileobj = None
        if flag_exists:
            if class_ == "messed":
                # Note that sp_ref may be None here if Cxxxx_spintg.fits fails to load
                # In this case, sp will have a default x-axis
                sp = ft.load_spectrum_fits_messed_x(fn, sp_ref)
                if sp:
                    fileobj = ft.FileSpectrum()
                    fileobj.spectrum = sp
            elif flag_supported:
                fileobj = class_()
                try:
                    fileobj.load(fn)
                except Exception as E:
                    a99.get_python_logger().exception("Error loading file '%s'" % fn)
                    error = str(E)

                if keyword == "spintg":
                    # Saves reference spectrum to use its x-axis to complete
                    # the "messed" files
                    sp_ref = fileobj.spectrum

            ret.append(BulkItem(keyword, fileobj, fn, flag_exists, flag_supported,
                            error))
    return ret


def create_spectrum_lists(dir_, pipeline_stage="spintg"):
    """
    Create several .splist files, grouping spectra by their wavelength vector

    Args:
        dir_: input & output directory
        pipeline_stage="spintg": input "stage", i.e., which stage of the pipeline will be loaded.
            Possible values:

            - "spintg": integrated spectrum (final stage)
            - "ifu_noseeing": take first spectrum of 7x1 data cube TODO explain
    """

    if pipeline_stage in ("spintg", "sky", "skysub"):

        def simid_to_spectrum(simid):
            fn = os.path.join(dir_, simid + "_{}.fits".format(pipeline_stage))
            fsp = ft.FileSpectrumFits()
            fsp.load(fn)
            return fsp.spectrum

    elif pipeline_stage == "ifu_noseeing":

        def simid_to_spectrum(simid):
            fn = os.path.join(dir_, simid + "_ifu_noseeing.fits")
            fsp = ft.FileFullCube()
            fsp.load(fn)
            return fsp.spectrum

    else:
        raise ValueError("Invalid or unsupported pipeline stage: '{}'".format(pipeline_stage))

    fnfn = glob.glob(os.path.join(dir_, "C*.par"))
    fnfn.sort()
    # # Loads everything that's needed from disk
    spectra = []  # [(FilePar0, Spectrum0), ...]
    for fn in fnfn:
        try:
            gg = re.search('C(\d+)', fn)
            if gg is None:
                raise RuntimeError(
                    "'.par' file name '%s' does not have pattern 'Cnnnnnn'" % fn)

            fp = ft.FilePar()
            fp.load(fn)

            sp = simid_to_spectrum(gg.group())

            spectra.append((fp, sp))
        except:
            a99.get_python_logger().exception(
                "Failed to add spectrum corresponding to file '%s'" % fn)

    # Groups files by their wavelength axis
    groups = []  # list of lists: [[(FilePar0, Spectrum0), ...], ...]
    for pair in spectra:
        if len(groups) == 0:
            groups.append([pair])
        else:
            flag_match = False
            for group in groups:
                wl0 = group[0][1].wavelength
                wl1 = pair[1].wavelength
                if len(wl0) == len(wl1) and np.all(wl0 == wl1):
                    flag_match = True
                    group.append(pair)
                    break
            if not flag_match:
                groups.append([pair])

    # Now creates the spectrum list files
    for h, group in enumerate(groups):

        # # Finds differences in simulation specifications
        # Finds names of parameters that differ at least in one file using set operations
        for i, (fp, _) in enumerate(group):
            s = set(fp.params.items())
            if i == 0:
                s_union = s
                s_overlap = s
            else:
                s_union = s_union | s
                s_overlap = s_overlap & s
        keys = list(dict(s_union - s_overlap).keys())
        key_dict = a99.make_fits_keys_dict(keys)

        # a99.get_python_logger().info("FITS headers to feature in all spectra:")
        # a99.get_python_logger().info(str(key_dict))


        fspl = ft.FileSpectrumList()
        nmin, nmax = 9999999, 0
        for fp, sp in group:
            try:
                gg = re.search('C(\d+)', fp.filename)
                if gg is None:
                    raise RuntimeError(
                        "'.par' file name '%s' does not have pattern 'Cnnnnnn'" % fp.filename)
                n = int(gg.groups()[0])
                nmin = min(n, nmin)
                nmax = max(n, nmax)

                # determines what to put in "ORIGIN" header
                origin = sp.more_headers.get("ORIGIN")
                origin = origin if origin else os.path.basename(sp.filename)

                # gets rid of all FITS headers (TODO not sure if this is a good idea yet)
                sp.clear_more_headers()
                sp.more_headers["ORIGIN"] = origin

                # copies to spectrum header all key-value pairs that differ among .par files
                for k in keys:

                    # unwanted parameters
                    # - simu name is redundant with simu_id
                    # - ext_link has info such as "Resource id #4"
                    if k in ["ext_link", "simu_name"]:
                        # TODO not efficient to have this here, should remove from keys
                        continue

                    value = fp.params.get(k)
                    if value is not None:
                        # Content-sensitive conversion
                        if k == "obj_ftemplate":
                            # Template filename comes with full local
                            # (i.e. Websim server) path, which is unnecessary
                            # for our identification
                            value = os.path.basename(value)
                        elif k == "psf_file":
                            # PSF filename also comes with its full path,
                            # which if probably irrelevant
                            value = os.path.basename(value)
                        # else:
                        #       # .get(k)

                    sp.more_headers[key_dict[k]] = value

                fspl.splist.add_spectrum(sp)
            except:
                a99.get_python_logger().exception(
                    "Failed to add spectrum corresponding to file '%s'" % fp.filename)

        fn = os.path.join(dir_, "group-%s-%02d-C%06d-C%06d.splist" % (pipeline_stage, h, nmin, nmax))
        fspl.save_as(fn)
        a99.get_python_logger().info("Created file '%s'" % fn)


def load_eso_sky():
    """Loads ESO sky model from data directory

    Returns:
        tuple: ``(emission, transmission)`` (two `f311.filetypes.Spectrum` objects)
    """
    from f311 import aosss as ao

    # From comments in file:
    # lam:     vacuum wavelength in micron
    # flux:    sky emission radiance flux in ph/s/m2/micron/arcsec2
    # dflux1:  sky emission -1sigma flux uncertainty
    # dflux2:  sky emission +1sigma flux uncertainty
    # dtrans:  sky transmission
    # dtrans1: sky transmission -1sigma uncertainty
    # dtrans2: sky transmission +1sigma uncertainty

    path_ = a99.get_path("data", "eso-sky.fits", module=ao)

    hl = fits.open(path_)
    d = hl[1].data

    x, y0, y1 = d["lam"]*10000, d["flux"], d["trans"]

    sp0 = ft.Spectrum()
    sp0.x, sp0.y = x, y0
    sp0.yunit = u.Unit("ph/s/m2/angstrom/arcsec2")

    sp1 = ft.Spectrum()
    sp1.x, sp1.y = x, y1

    return sp0, sp1
