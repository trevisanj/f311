import f311.filetypes as ft
import datetime

__all__ = ["make_file_molecules"]


def make_file_molecules(mol_row, state_consts, lines, qgbd_calculator, sols_calculator):
    """

    Args:
        mol_row: MyDBRow object representing row from 'molecules' table
        state_consts: dict-like object with keys "omega_e", etc.
        lines: molecular lines data; type/format varies depending on type of data
        qgbd_calculator: callable(state_consts, v_lo) that can calculate "qv", "gv", "bv", "dv",
                         e.g., calc_qbdg_tio_like()
        sols_calculator: callable(state_consts, lines, qgbd_calculator) that returns a list of
                         SetOfLines, e.g., hitran_to_sols()

    Returns: (a FileMolecules object, a MolConversionLog object)
    """

    sols, log = sols_calculator(mol_row, state_consts, lines, qgbd_calculator)
    mol = ft.mol_row_to_molecule(mol_row)
    mol.sol = sols
    f = ft.FileMolecules()
    f.titm = "Created by ftpyfant.make_file_molecules() @ {}".format(datetime.datetime.now().isoformat())
    f.molecules = [mol]

    return f, log

