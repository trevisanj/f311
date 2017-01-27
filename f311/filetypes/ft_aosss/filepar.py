__all__ = ["FilePar"]


import a99
from .. import DataFile
from collections import OrderedDict


@a99.froze_it
class FilePar(DataFile):
    """WebSim-COMPASS ".par" (parameters) file"""

    description = "Session parameters"
    default_filename = None
    attrs = ["params"]

    def __init__(self):
        DataFile.__init__(self)
        self.params = OrderedDict()

    def __getitem__(self, key):
        return self.params[key]

    def _do_load(self, filename):
        data = []  # keyword, value pairs create dict at the end
        with open(filename, "r") as f:
            for i, line in enumerate(f):
                s = line.strip()

                if i == 0:
                    # Magic check: is it really a FilePar?
                    if not s.startswith("# parameter profile"):
                        raise RuntimeError("Not a '.par' file")

                if s.startswith("#"):
                    continue
                if len(s) == 0:
                    continue

                KEYWORD_LENGTH = 26
                keyword = s[:KEYWORD_LENGTH].strip()
                value = s[KEYWORD_LENGTH:]
                data.append((keyword, value))

        self.params = OrderedDict(data)

    def _do_save_as(self, filename):
        raise RuntimeError("Not applicable")

