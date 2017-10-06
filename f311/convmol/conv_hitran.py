"""
HITRAN-specific conversion

References:
  [1] Rothman, Laurence S., et al. "The HITRAN 2004 molecular spectroscopic database."
      Journal of Quantitative Spectroscopy and Radiative Transfer 96.2 (2005): 139-204.
  [2] extraehitran.f (First version: Jorge Melendez-Moreno, January 1999)
"""


import f311.physics as ph
import f311.filetypes as ft
import a99
from .calc_qgbd import calc_qgbd_tio_like
from .convlog import *
from collections import OrderedDict

__all__ = ["hitran_to_sols"]


_OH_BRANCH_MAP_OH = {"QQ": "Q", "PP": "P", "RR": "R"}



def _parse_local_lower_quanta_OH(Q2l):
    """
    Parses the "Lower-state 'local' quanta" for 'OH' (see [1], Table 4, group 2, observation 'b')

    Args:
        Q2l: 15-character string containing the lower-state 'local' quanta information of molecular
        line. Example: " PP 12.5ff     "

    Returns: (Br, J2l), where
        Br: branch ("P"/"Q"/"R")
        J2l: inferior "quantum number associated with the total angular momentum excluding nuclear
             spin" [1]

    **Note** will raise if cannot determine Br (branch)
    """
    brinfo = Q2l[1:3]
    Br = _OH_BRANCH_MAP_OH.get(brinfo)
    if Br is None:
        raise ValueError("Cannot derive branch from '{}' ((local lower quanta) = '{}')".
                         format(brinfo, Q2l))
    J2l = float(Q2l[3:8])
    return Br, J2l

def _parse_local_lower_quanta_group2(Q2l):
    """
    Parses the "lower-state 'local' quanta" for molecules in [1], Table 4, group 2

    Args, Returns: see _parse_local_lower_quanta_OH()
    """

    # TODO test, not sure
    Br = Q2l[5:6]
    J2l = float(Q2l[6:9])
    return Br, J2l


def _parse_local_lower_quanta_group6(Q2l):
    """[...] [1], Table 4, group 6"""

    # TODO test, not sure
    Br = Q2l[3:4]
    J2l = float(Q2l[4:9])
    return Br, J2l


def _parse_global_quanta_class1(V):
    """
    Parses the [upper/lower] "global quanta" ([1], Table 3, class 1

    Args:
        V: 15-character string containing the 'global' quanta information of molecular
           line. Example: "       X3/2   8"

    Returns: v1: "quantum number associated with the first normal mode of vibration" [1]
    """
    return int(V[13:15])


def _parse_global_quanta_class2(V):
    """[...] [1], Table 3, class 2"""
    return int(V[13:15])

def _parse_global_quanta_class3(V):
    return int(V[13:15])


__GROUP_MAP = (
    (("OH",),
     _parse_local_lower_quanta_OH),
    (("CO2", "N2O", "CO", "HF", "HCl", "HBr", "HI", "OCS", "N2", "HCN", "C2H2", "NO+"),
     _parse_local_lower_quanta_group2),
    (("NO", "ClO"),
     _parse_local_lower_quanta_group6),
)
_GROUP_DICT = dict(sum([[(mol, callable_) for mol in mols] for mols, callable_ in __GROUP_MAP], []))

__CLASS_MAP = (
    (("CO", "HF", "HCl", "HBr", "HI", "N2", "NO+"), _parse_global_quanta_class1),
    (("O2",), _parse_global_quanta_class2),
    (("NO", "OH", "ClO"), _parse_global_quanta_class3),
)
_CLASS_DICT = dict(sum([[(mol, callable_) for mol in mols] for mols, callable_ in __CLASS_MAP], []))


def hitran_to_sols(molconsts, lines, qgbd_calculator):
    """
    Converts HITRAN molecular lines data to PFANT "sets of lines"

    Args:
        molconsts: a dict-like object combining field values from tables 'molecule', 'state',
                    'pfantmol', and 'system' from a FileMolDB database
        lines: item from rom hapi.LOCAL_TABLE_CACHE (a dictionary)
        qgbd_calculator: callable that can calculate "qv", "gv", "bv", "dv",
                         e.g., calc_qbdg_tio_like()

    Returns: (a list of ftpyfant.SetOfLines objects, a MolConversionLog object)
    """

    def append_error(msg):
        log.errors.append("#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), str(msg)))

    # C     BAND (v',v'')=(VL,V2L)
    # C     WN: vacuum wavenumber   WL : air wavelength
    # C     J2L: lower state angular momentum number
    # C     iso: isotope/ 26: 12C16O, 36: 13C16O, 27: 12C17O, 28: 12C18O
    # C     ramo: branch, for P: ID=1, for R: ID=2
    # C     name: file name/ coisovLv2L
    # C     HL: Honl-London factor
    # C     FR: oscillator strength

    header = lines["header"]
    data = lines["data"]

    S = molconsts.get_S2l()
    DELTAK = molconsts.get_deltak()
    formula = molconsts["formula"]

    n = header["number_of_rows"]
    log = MolConversionLog(n)
    sols = OrderedDict()  # one item per (vl, v2l) pair

    try:
        f_class = _CLASS_DICT[formula]
    except KeyError:
        log.errors.append("Cannot determine Table 3 'class' (Rothman et al. 2005) for formula '{}'".
                          format(formula))
        log.flag_ok = False

    try:
        f_group = _GROUP_DICT[formula]
    except KeyError:
        log.errors.append("Cannot determine Table 4 'group' (Rothman et al. 2005) for formula '{}'".
                          format(formula))
        log.flag_ok = False

    if not log.flag_ok:
        return [], log

    for i in range(n):

        try:
            nu = data["nu"][i]
            wl = ph.vacuum_to_air(1e8/nu)
            Br, J2l = f_group(data["local_lower_quanta"][i])
            # TODO assuming singlet!!!
            Jl = ph.singlet.quanta_to_branch(Br, J2l)
            V = f_class(data["global_upper_quanta"][i])
            V_ = f_class(data["global_lower_quanta"][i])
            A = data["a"][i]

            # A seguir normalizacion de factor de Honl-london (HLN)
            # TODO ask BLB: is this formula always like this?
            Normaliza = 1/((2.0*J2l+1)*(2.0*S+1)*(2.0-DELTAK))

            # A seguir teremos a forca de oscilador
            # mas q sera normalizada segundo o programa da Beatriz
            # TODO ask BLB: what we call the Honl-London factor, he calls the "forca de oscilador"
            gf = Normaliza*1.499*(2*Jl+1)*A/(nu**2)

            J2l_pfant = int(J2l)  # ojo, estamos colocando J2L-0.5! TODO ask BLB: we write J2l or J2l-.5?
        except Exception as e:
            log.errors.append("#{}{} line: {}".format(i+1, a99.ordinal_suffix(i+1), a99.str_exc(e)))
            continue

        sol_key = (V, V_)  # (v', v'') transition (v_sup, v_inf)
        if sol_key not in sols:
            qgbd = qgbd_calculator(molconsts, sol_key[1])
            qqv = qgbd["qv"]
            ggv = qgbd["gv"]
            bbv = qgbd["bv"]
            ddv = qgbd["dv"]

            sols[sol_key] = ft.SetOfLines(V, V_, qqv, ggv, bbv, ddv, 1.)
        sol = sols[sol_key]
        sol.append_line(wl, gf, J2l_pfant, Br)

    return (list(sols.values()), log)
