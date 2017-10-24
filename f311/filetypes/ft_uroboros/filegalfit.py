import a99
from .. import DataFile
from astropy.io import fits
from collections import defaultdict, Counter

__all__ = ["FileGalfit"]

@a99.froze_it
class FileGalfit(DataFile):
    """FITS file with frames named INPUT_*, MODEL_*, RESIDUAL_*, which is the output of Galfit software

    When file is loaded, the band_names property will be filled

    IF INPUT_*, MODEL_* and RESIDUAL_* do not have the same band names, the file is "rejected"
    """
    attrs = []
    description = "Galfit output"
    default_filename = None
    flag_txt = False

    @property
    def band_names(self):
        return self._band_names

    @property
    def kind_names(self):
        return self._kind_names

    def __init__(self):
        DataFile.__init__(self)
        self.hdulist = None
        self._band_names = []
        self._kind_names = []
        # Frame indexes by key (kind_name, band_name)
        self._idxs = {}

    def get_frame(self, kind_name, band_name):
        """Convenience function to get frame using its "kind name", "band name"

        Args:
            kind_name: str in self.kind_names
            band_name: str in self.band_names
        """
        return self.hdulist[self._idxs[(kind_name, band_name)]]



    def _do_load(self, filename):
        f = fits.open(filename)

        info = f.info(False)


        # Example:
        #     [(0, 'PRIMARY', 'PrimaryHDU', 8, (720, 720), 'float32', ''),
        #      (1, 'INPUT_fuv', 'ImageHDU', 40, (720, 720), 'float64', ''),
        #      (2, 'INPUT_nuv', 'ImageHDU', 40, (720, 720), 'float64', ''),
        #      (3, 'INPUT_r', 'ImageHDU', 42, (720, 720), 'float64', ''),
        #      (4, 'INPUT_j', 'ImageHDU', 41, (720, 720), 'float64', ''),
        #      (5, 'INPUT_h', 'ImageHDU', 41, (720, 720), 'float64', ''),
        #      (6, 'INPUT_k', 'ImageHDU', 41, (720, 720), 'float64', ''),
        #      (7, 'INPUT_3.4', 'ImageHDU', 35, (720, 720), 'float64', ''),
        #      (8, 'INPUT_4.6', 'ImageHDU', 35, (720, 720), 'float64', ''),
        #      (9, 'MODEL_fuv', 'ImageHDU', 409, (720, 720), 'float32', ''),
        #      (10, 'MODEL_nuv', 'ImageHDU', 409, (720, 720), 'float32', '')

        kinds = defaultdict(lambda: [])
        kind_names = ("INPUT", "MODEL", "RESIDUAL")
        counts = Counter()
        idxs = {}

        for record in info[1:]:  # skips "PRIMARY"
            index = record[0]
            name = record[1]
            if name.startswith(kind_names):
                counts[kind_name] += 1
                kind_name, band_name = name.split("_")
                kinds[kind_name].append(band_name)
                idxs[(kind_name, band_name)] = index

        # Validation: must find at least one INPUT, one MODEL, and one RESIDUAL
        for kind_name in kind_names:
            if kind_name not in counts:
                raise RuntimeError("Cannot find a frame containing the word '{}' in its name".format(kind_name))

        # Validation: band names of all kinds must match
        if kinds["INPUT"] != kinds["MODEL"]:
            raise RuntimeError("(INPUT, MODEL) band names mismatch: {} != {}".
                               format(kinds["INPUT"], kinds["MODEL"]))
        if kinds["INPUT"] != kinds["RESIDUAL"]:
            raise RuntimeError("(INPUT, RESIDUAL) band names mismatch: {} != {}".
                               format(kinds["INPUT"], kinds["RESIDUAL"]))


        self._band_names = kinds["INPUT"]
        self._kind_names = kind_names
        self._idxs = idxs

        self.hdulist = f

    def _do_save_as(self, filename):
        a99.overwrite_fits(self.hdulist, filename)
