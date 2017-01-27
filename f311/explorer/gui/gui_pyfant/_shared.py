"""
Constants shared among windows, and resources that are not general enough to be put in API
"""


# No need to implementa a "__all__", a99 will be del'ed at the end
import a99


# Color for labels indicating a star parameter
COLOR_STAR = "#2A8000"
# Color for labels indicating a software configuration parameter
COLOR_CONFIG = "#BD6909"


# Messages shared in two or more different situations
INITIALIZES_SUN = "Initializes fields with default parameters (Sun)"
PARAMS_INVALID = "Can't save, invalid parameter values(s)!"
LLZERO_LLFIN = "The calculation interval for the synthetic spectrum is given by "\
  "["+a99.enc_name("llzero", COLOR_CONFIG)+", "+a99.enc_name("llfin", COLOR_CONFIG)+"]."\
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

del a99