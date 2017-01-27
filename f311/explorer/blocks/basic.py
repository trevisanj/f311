_all_ = ["SpectrumBlock", "ToScalar", "SpectrumListBlock", "GroupBlock"]


import numpy as np
import copy
import f311.filetypes as ft


########################################################################################################################

class _BaseBlock(object):
    def __init__(self):
        self._input = None

    def use(self, inp):
        self._input = inp
        try:
            output = self._do_use(inp)
            return output
        finally:
            self._input = None

    def _do_use(self, inp):
        raise NotImplementedError()


class _SpectrumBlock(_BaseBlock):
    """Input is Spectrum (abbreviated "SB")"""

    def use(self, inp):
        assert isinstance(inp, ft.Spectrum)
        self._input = inp
        try:
            # If the output wavelength vector is the same, flag_copy_wavelength determines whether this vector
            # will be copied or just assigned to the output
            #
            # **Attention** blocks that handle the wavelength vectors must comply
            output = self._do_use(inp)
            assert output is not None  # it is common to forger to return in _do_use()
            if isinstance(output, ft.Spectrum):
                assert output._flag_created_by_block
            # Automatically assigns output wavelength vector if applicable
            if isinstance(output, ft.Spectrum) and output.wavelength is None and len(output.y) == len(inp.y):
                output.wavelength = np.copy(inp.wavelength)  # TODO this may slow down things... or not ... if self.flag_copy_wavelength else input.wavelength
            return output
        finally:
            self._input = None


class SpectrumBlock(_SpectrumBlock):
    """Spectrum-To-Spectrum"""

    def use(self, inp):
        assert isinstance(inp, ft.Spectrum)
        self._input = inp
        try:
            # If the output wavelength vector is the same, flag_copy_wavelength determines whether this vector
            # will be copied or just assigned to the output
            #
            # **Attention** blocks that handle the wavelength vectors must comply
            output = self._do_use(inp)
            assert output is not None  # it is common to forger to return in _do_use()
            assert isinstance(output, ft.Spectrum)
            assert output._flag_created_by_block
            # Automatically assigns output wavelength vector if applicable
            if isinstance(output, ft.Spectrum) and output.wavelength is None and len(output.y) == len(inp.y):
                output.wavelength = np.copy(inp.wavelength)  # TODO this may slow down things... or not ... if self.flag_copy_wavelength else input.wavelength
            return output
        finally:
            self._input = None

    def _new_output(self):
        """Call from _do_use() to create new spectrum based on input spectrum.

        Never create spectrum directly because we want to keep certain attributes, such as more_headers"""
        output = ft.Spectrum()
        output._flag_created_by_block = True  # assertion
        output.more_headers = copy.deepcopy(self._input.more_headers)
        return output

    def _copy_input(self, inp):
        """
        Returns copy of input + extra annotations

        Don't copy spectra explicitly; use this method instead
        """

        output = copy.deepcopy(inp)
        output._flag_created_by_block = True

        return output

    def _do_use(self, inp):
        """Default implementation is identity"""
        return self._copy_input(inp)


class ToScalar(_SpectrumBlock):
    """Ancestor for Spectrum Blocks whose output is a scalar (abbreviated "SpToSca")"""


class _SpectrumListBlock(_BaseBlock):
    """SpectrumBlock -- class with a "use" method accepting a SpectrumList as input"""

    def use(self, inp):
        assert isinstance(inp, ft.SpectrumList)
        self._input = inp
        try:
            output = self._do_use(inp)
            assert output is not None
            if isinstance(output, ft.SpectrumList):
                assert output._flag_created_by_block
            return output
        finally:
            self._input = None

    def _new_output(self):
        """Call from _do_use() to create new SpectrumList based on input"""
        output = ft.SpectrumList()
        output._flag_created_by_block = True  # assertion
        return output

    def _do_use(self, inp):
        """Default implementation is identity"""
        return inp


class SpectrumListBlock(_SpectrumListBlock):
    """Blocks whose output have the same number of spectra as the input (abbreviated "SpectrumListBlock")"""


class GroupBlock(_SpectrumListBlock):
    """
    Blocks whose output have only one spectrum (abbreviated "MDB")

    The "merge down" idea is that output from these blocks have only one spectrum
    (still stored as a spectrum list though)

    This class has no gear and exists for grouping purposes only
    """
