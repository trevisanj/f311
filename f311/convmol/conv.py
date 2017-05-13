from .calc_qgbd import *
from .convlog import *
import datetime

__all__ = ["Conv"]



class Conv(object):
    # TODO there is a good chance that flag_hlf, flag_fcf, etc. will be moved to this class
    """Molecular lines converter base class

    Args:
        qgbd_calculator: callable that can calculate "qv", "gv", "bv", "dv",
                         Default: calc_qbdg_tio_like

        mol_consts: a dict-like object combining field values from tables 'molecule', 'state',
                    'pfantmol', and 'system' from a FileMolDB database

        fcfs: Franck-Condon Factors (dictionary of floats indexed by (vl, v2l))
    """

    def __init__(self, qgbd_calculator=None, mol_consts=None, fcfs=None):
        self.qgbd_calculator = qgbd_calculator if qgbd_calculator else calc_qgbd_tio_like
        self.mol_consts = mol_consts
        self.fcfs = fcfs

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
        assert isinstance(sols, list)
        assert isinstance(log, MolConversionLog)

        sols.sort(key= lambda sol: sol.vl*1000+sol.v2l)


        mol = ft.mol_consts_to_molecule(self.mol_consts)
        mol.sol = sols
        f = ft.FileMolecules()
        now = datetime.datetime.now()
        f.titm = "Created by ftpyfant.make_file_molecules() @ {}".format(now.isoformat())
        f.molecules = [mol]
        return f, log

    # Must reimplement thig
    def _make_sols(self, lines):
        """Converts molecular lines into a list of SetOfLines object

        Args:
            lines: see make_file_molecules()

        Returns:
            sols, log: list of SefOfLines object, MolConversionLog object
        """
        raise NotImplementedError()

    def _calculate_qgbd(self, v2l):
        return self.qgbd_calculator(self.mol_consts, v2l)
