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
        # Opening with encoding other than 'utf-8' to avoid the following error:
        #
        #     UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb0 in position 1782: invalid start byte
        with open(filename, "r", encoding='windows-1252') as f:
            i = 0
            try:
                for line in f:
                    s = line.strip()

                    if i == 0:
                        # Magic check: is it really a FilePar?
                        if not s.startswith("# parameter profile"):
                            raise RuntimeError("File '{}' is not a '.par' file".format(filename))

                    if s.startswith("#"):
                        pass
                    elif len(s) == 0:
                        pass
                    else:
                        KEYWORD_LENGTH = 26
                        keyword = s[:KEYWORD_LENGTH].strip()
                        value = s[KEYWORD_LENGTH:]
                        data.append((keyword, value))

                    i += 1
            except Exception as e:
                raise RuntimeError("In line {} of file '{}'".format(i+1, filename)) from e

        self.params = OrderedDict(data)

    def _do_save_as(self, filename):
        raise RuntimeError("Not applicable")

