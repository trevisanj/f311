"""
Transition-specific calculations

References:
  [1] agrup.plez7.f
"""

from collections import OrderedDict


__all__ = ["calc_qgbd_tio_like"]


def calc_qgbd_tio_like(state_consts, v_lo):
    """
    Calculates qv, gv, bv, dv in TiO-like fashion

    Based on Fortran source 'agrup.plez7.f'

    Args:
        state_consts: dict-like object with keys:
            "omega_e"
            "omega_ex_e"
            "omega_ey_e"
            "B_e"
            "alpha_e"
            "D_e"
            "beta_e"

        v_lo: (integer) low transition level

    Returns: qbdg, i.e., a dictionary with keys:
            "qv", "gv", "bv", "dv", "gzero"
    """

    omega_e = state_consts["omega_e"]
    omega_ex_e = state_consts["omega_ex_e"]
    omega_ey_e = state_consts["omega_ey_e"]
    B_e = state_consts["B_e"]
    D_e = state_consts["D_e"]
    alpha_e = state_consts["alpha_e"]
    beta_e = state_consts["beta_e"]

    if int(v_lo) != v_lo:
        raise ValueError("Argument 'v_lo' must be an integer")

    gzero = omega_e / 2.0 - omega_ex_e / 4.0 + omega_ey_e / 8.0
    v_lo5 = v_lo + 0.5

    # Franck-Condon factor
    # TODO: calculate the Franck-Condon factor
    qv = 1.
    # rotational constant "B_v"
    bv = B_e - alpha_e * v_lo5
    # rotational constant "D_v"
    dv = (D_e + beta_e * v_lo5) * 1.0e+06
    # rotational term " G_A"
    gv = omega_e * v_lo5 - omega_ex_e * v_lo5 ** 2 + omega_ey_e * v_lo5 ** 3 - gzero

    qgbd = OrderedDict((("qv", qv), ("gv", gv), ("bv", bv), ("dv", dv), ("gzero", gzero)))

    return qgbd
