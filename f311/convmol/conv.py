import f311.physics as ph
import f311.filetypes as ft
from .calc_qgbd import *
from .convlog import *
import datetime
from collections import OrderedDict
import math


__all__ = ["Conv", "ConvSols"]


_DEFAULT_QGBD_CALCULATOR = calc_qgbd_tio_like


class ConvSols(OrderedDict):
    """Stores (vl, v2l) as keys, SetOfLines as values"""

    def __init__(self, qgbd_calculator, molconsts):
        OrderedDict.__init__(self)
        self.qgbd_calculator = qgbd_calculator if qgbd_calculator else _DEFAULT_QGBD_CALCULATOR
        self.molconsts = molconsts

    def append_line(self, line, gf_pfant, branch):
        """Use to append line to object"""
        sol_key = (line.vl, line.v2l)

        if sol_key not in self:
            qgbd = self.qgbd_calculator(self.molconsts, line.v2l)
            self[sol_key] = ft.SetOfLines(line.vl, line.v2l,
                                          qgbd["qv"], qgbd["gv"], qgbd["bv"], qgbd["dv"], 1.)

        self[sol_key].append_line(line.lambda_, gf_pfant, line.J2l, branch)


class Conv(object):
    # TODO there is a good chance that flag_hlf, flag_fcf, etc. will be moved to this class
    """Molecular lines converter base class

    Args:
        qgbd_calculator: callable that can calculate "qv", "gv", "bv", "dv",
                         Default: calc_qbdg_tio_like

        molconsts: a dict-like object combining field values from tables 'molecule', 'state',
                    'pfantmol', and 'system' from a FileMolDB database

        fcfs: Franck-Condon Factors (dictionary of floats indexed by (vl, v2l))
    """

    def __init__(self, qgbd_calculator=None, molconsts=None, flag_normhlf=True, fcfs=None):
        self.qgbd_calculator = qgbd_calculator if qgbd_calculator else calc_qgbd_tio_like
        self.molconsts = molconsts
        self.fcfs = fcfs
        self.flag_normhlf = flag_normhlf

    def make_file_molecules(self, lines):
        """
        Builds a FileMolecules object

        Args:
            lines: in most cases, a DataFile instance, but may be anything, since the molecular
                   lines data extraction is performed by a particular descendant class.
                   For example, the HITRAN converter expects a structure from the HAPI

        Returns:
            f, log: FileMolecules, MolConversionLog instances
        """
        from f311 import filetypes as ft

        # Runs specific conversor to SetOfLines
        sols, log = self._make_sols(lines)

        assert isinstance(sols, ConvSols)
        assert isinstance(log, MolConversionLog)

        sols_list = list(sols.values())
        sols_list.sort(key= lambda sol: sol.vl*1000+sol.v2l)

        mol = ft.molconsts_to_molecule(self.molconsts)
        mol.sol = sols_list
        f = ft.FileMolecules()
        now = datetime.datetime.now()
        f.titm = "PFANT molecular lines file. Created by f311.convmol.Conv.make_file_molecules() @ {}".format(now.isoformat())
        f.molecules = [mol]
        return f, log

    def multiplicity_toolbox(self):
        """Wraps f311.physics.multiplicity.multiplicity_toolbox()"""
        return ph.multiplicity_toolbox(self.molconsts, flag_normalize=self.flag_normhlf)

    # Must reimplement thig
    def _make_sols(self, lines):
        """Converts molecular lines into a list of SetOfLines object

        Args:
            lines: see make_file_molecules()

        Returns:
            sols, log: ConvSols, MolConversionLog
        """
        raise NotImplementedError()

    ######
    # Gear

    def _calculate_qgbd(self, v2l):
        return self.qgbd_calculator(self.molconsts, v2l)

    def _get_fcf(self, vl, v2l, flag_special=False):
        try:
            fcf = self.fcfs[(vl, v2l)]

            if flag_special:
                fcf = fcf * 10 ** -(math.floor(math.log10(fcf)) + 1)

        except KeyError as e:
            raise KeyError("FCF not available for (vl, v2l) = ({}, {})".format(vl, v2l))
        return fcf
