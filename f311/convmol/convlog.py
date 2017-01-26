class MolConversionLog(object):
    def __init__(self, num_lines_in=0, errors=[], flag_ok=True):
        self.errors = errors
        # Number of input lines
        self.num_lines_in = num_lines_in
        # Whether the conversion was considered successful (despite errors)
        self.flag_ok = flag_ok

    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, self.num_lines_in, self.errors,
                                       self.flag_ok)
    