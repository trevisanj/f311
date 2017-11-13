"""
Transition-specific calculations

References:
  [1] agrup.plez7.f
"""

from collections import OrderedDict


__all__ = ["calc_qgbd_tio_like"]


def calc_qgbd_tio_like(molconsts, v_lo):
    """
    Calculates qv, gv, bv, dv in TiO-like fashion

    Based on Fortran source 'agrup.plez7.f'

    Args:
        molconsts: dict-like object with keys:
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

    omega_e = molconsts["state2l_omega_e"]
    omega_ex_e = molconsts["state2l_omega_ex_e"]
    omega_ey_e = molconsts["state2l_omega_ey_e"]
    B_e = molconsts["state2l_B_e"]
    D_e = molconsts["state2l_D_e"]
    alpha_e = molconsts["state2l_alpha_e"]
    beta_e = molconsts["state2l_beta_e"]

    if int(v_lo) != v_lo:
        raise ValueError("Argument 'v_lo' must be an integer")

    gzero = omega_e / 2.0 - omega_ex_e / 4.0 + omega_ey_e / 8.0
    v_lo5 = v_lo + 0.5

    # Franck-Condon factor. Currently always incorporated into "SJ"
    qv = 1.
    # rotational constant "B_v"
    bv = B_e - alpha_e * v_lo5
    # rotational constant "D_v"
    dv = (D_e + beta_e * v_lo5) * 1.0e+06
    # rotational term " G_A"
    gv = omega_e * v_lo5 - omega_ex_e * v_lo5 ** 2 + omega_ey_e * v_lo5 ** 3 - gzero

    qgbd = OrderedDict((("qv", qv), ("gv", gv), ("bv", bv), ("dv", dv), ("gzero", gzero)))

    return qgbd
