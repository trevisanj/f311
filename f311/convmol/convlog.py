from collections import Counter
import a99

@a99.froze_it
class MolConversionLog(object):

    @property
    def num_lines_skipped(self):
        """Sums all counts in self.skip_reasons"""
        return sum(self.skip_reasons.values())


    def __init__(self, num_lines=0, flag_ok=True):
        # Number of lines in input file
        self.num_lines = num_lines
        # Whether the conversion was considered successful (despite errors)
        self.flag_ok = flag_ok
        # List of error strings
        self.errors = []
        # Counter: {"reason": number_of_times, ...}
        # The key should be a descriptive reason, however shortish
        # Access like this:
        #     >>> log.skip_reasons["FCF not found for (vl,v2l)"] += 1
        #
        self.skip_reasons = Counter()

