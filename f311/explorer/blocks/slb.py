__all__ = ["SLB_UseSpectrumBlock", "SLB_ExtractContinua"]

import numpy as np
import a99
import copy
from .basic import *
from . import sb

class SLB_UseSpectrumBlock(SpectrumListBlock):
    """Calls sblock.use() for each individual spectrum"""

    def __init__(self, sblock=None):
        SpectrumListBlock.__init__(self)
        self.sblock = sblock

    def _do_use(self, inp):
        output = self._new_output()
        for i, sp in enumerate(inp.spectra):
            output.add_spectrum(self.sblock.use(sp))
        return output


class SLB_ExtractContinua(SpectrumListBlock):
    """Calculates upper envelopes and subtracts mean(noise std)"""

    # TODO this is not a great system. Just de-noising could substantially improve the extracted continua

    def _do_use(self, inp):
        from . import gb
        output = SLB_UseSpectrumBlock(sb.SB_Rubberband(flag_upper=True)).use(inp)
        spectrum_std = gb.GB_UseNumPyFunc(func=np.std).use(inp)
        mean_std = np.mean(spectrum_std.spectra[0].y)
        for spectrum in output.spectra:
            spectrum.y -= mean_std * 3
        return output


class SLB_UseGroupBlock(SpectrumListBlock):
    """
    "Group by" operation using a GroupBlock

    Args:
        block: a GroupBlock
        group_by: sequence of spectrum "more_headers" fieldnames.
                  If not passed, will treat the whole SpectrumCollection as a single gb.py.
                  If passed, will split the collection in groups and perform the "merge down" operations separately
                  for each gb.py

    Returns: (SpectrumCollection containing query result, list of error strings)
    """

    def __init__(self, block, group_by=None):
        SpectrumListBlock.__init__(self)
        assert isinstance(block, GroupBlock)
        self.block = block
        self.group_by = group_by

    def _do_use(self, inp):

        # Creates the groups
        if not self.group_by:
            out = self.block.use(inp)
        else:
            groups = []

            grouping_keys = [
                tuple([spectrum.more_headers.get(fieldname) for fieldname in self.group_by]) for
                spectrum in inp.spectra]

            unique_keys = list(set(grouping_keys))
            unique_keys.sort()
            sk = list(zip(inp.spectra, grouping_keys))
            for unique_key in unique_keys:
                group = ft.SpectrumList()
                for spectrum, grouping_key in sk:
                    if grouping_key == unique_key:
                        group.add_spectrum(spectrum)
                groups.append(group)

            out = self._new_output()
            out.fieldnames = self.group_by  # new SpectrumList will have the gb.py field names

            # Uses block in each gb.py
            for group in groups:
                splist = self.block.use(group)

                # copies "gb.py by" fields from first input spectrum to output spectrum
                sp = splist.spectra[0]
                for fieldname in self.group_by:
                    sp.more_headers[fieldname] = group.spectra[0].more_headers[fieldname]

                out.merge_with(splist)

        return out
