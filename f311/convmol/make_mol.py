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
    mol = _make_molecule(mol_row, sols)
    f = ft.FileMolecules()
    f.titm = "Created by ftpyfant.make_file_molecules() @ {}".format(datetime.datetime.now().isoformat())
    f.molecules = [mol]

    return f, log


def _make_molecule(mol_row, sols):
    """Assembles a Molecule object taking all necessary information

    Args:
        mol_row: MyDBRow object representing row from 'molecules' table
        mol_consts: dict-like object with keys "fe", "do", "am", "bm", "ua", "ub", "te"
        sol: ftpyfant.SetOfLines object

    **Note** Doesn't take take "fe", "do", etc. directly from the 'molecule' table because these
             values may have been customized by the user in widget WMolConst
    """

    mol = ft.Molecule()
    mol.description = "{name} ({formula})".format(**mol_row)
    mol.symbols = [mol_row["symbol_a"], mol_row["symbol_b"]]
    mol.fe = mol_row["fe"]
    mol.do = mol_row["do"]
    mol.mm = mol_row["am"] + mol_row["bm"]
    mol.am = mol_row["am"]
    mol.bm = mol_row["bm"]
    mol.ua = mol_row["ua"]
    mol.ub = mol_row["ub"]
    mol.te = mol_row["te"]
    mol.cro = mol_row["cro"]
    mol.s = mol_row["s"]

    mol.sol = sols

    return mol