from .. import FilePyConfig, ConfigDict
import a99
from collections import defaultdict

__all__ = ["FileConfigConvMol"]


@a99.froze_it
class FileConfigConvMol(FilePyConfig):
    """Python source containing 'config_conv = ConfigConv(...)"""

    description = "configuration file for molecular lines conversion GUI"
    default_filename = "configconvmol.py"
    attrs = ["obj"]
    editors = []

    # Name of variable in module
    modulevarname = "ccm"
