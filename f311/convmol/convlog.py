class MolConversionLog(object):
    def __init__(self, num_lines=0, errors=None, flag_ok=True, num_lines_skipped=0):
        self.errors = [] if errors is None else errors
        # Number of lines in input file
        self.num_lines = num_lines
        # Whether the conversion was considered successful (despite errors)
        self.flag_ok = flag_ok
        # Number of lines skipped because of some filtering criterion
        self.num_lines_skipped = num_lines_skipped

    