"""
Constants shared among windows, and resources that are not general enough to be put in API
"""


import a99
import f311.pyfant as pf


# Messages shared in two or more different situations
INITIALIZES_SUN = "Initializes fields with default parameters (Sun)"
PARAMS_INVALID = "Can't save, invalid parameter values(s)!"
LLZERO_LLFIN = "The calculation interval for the synthetic spectrum is given by "\
  "["+a99.enc_name("llzero", pf.COLOR_CONFIG)+", "+a99.enc_name("llfin", pf.COLOR_CONFIG)+"]."\
"""
<pre>
          aint
          &lt;--&gt;

----[----|----|----|----|-]-------&gt;
    |                     |       wavelength (angstrom)
    llzero                llfin
</pre>
"""

DESCR_PTDISK = """
This option is used to simulate a spectrum acquired
out of the center of the star disk.<br><br>
This is useful if the synthetic spectrum will be compared with an
observed spectrum acquired out of the center of the star disk.
<ul>
    <li>True: 7-point integration
    <li>False: 6- or 26-point integration, depending on option --kik
</ul>"""


DESCR_MULTI = """
Runs pfant for different abundances for each element, then run nulbad for each
pfant result for different FWHMs.

The configuration is read from a .py file.

The user must specify a list of FWHM values for nulbad convolutions, and
a dictionary containing element symbols and respective list containing n_abdif
differential abundances to be used for each element.

pfant will be run n_abdif times, each time adding to each element in ab the i-th
value in the vector for the corresponding element.

nulbad will run n_abdif*n_fwhms times, where n_fwhms is the number of different
FWHMs specified.

The result will be
- several spectra saved as  "<star name><pfant name or counter>.sp"
- several "spectra list" files saved as "cv_<FWHM>.spl". As the file indicates,
  each ".spl" file will have the names of the spectrum files for a specific FWHM.
  .spl files are subject to input for lineplot.py by E.Cantelli
"""


# Relating tablewidget column headers with set-of-lines attributes
# This is shared between XFileMolecules and XMolLinesEditor
SOL_HEADERS = ["lambda", "sj", "jj", "branch"]
SOL_HEADERS_PLOT = ["lambda", "sj", "jj"]
SOL_ATTR_NAMES = ["lmbdam", "sj", "jj", "branch"]


# Relating tablewidget column headers with Atom atributes
# This is shared between XFileAtoms and XAtomLinesEditor
ATOM_HEADERS = ["lambda", "kiex", "algf", "ch", "gr", "ge", "zinf"]
ATOM_ATTR_NAMES = ["lambda_", "kiex", "algf", "ch", "gr", "ge", "zinf"]


class PlotInfo(object):
    """Just a data container class, used by both the Atomic and Molecular lines editors"""
    def __init__(self):
        self.flag = True  # Whether the plot is supposed to be shown or not
        self.mpl_obj = None  # matplotlib Lines2D object
        self.axis = None  # matplotlib axis
        self.y_vector = None  # reference to sol.sj or jj
