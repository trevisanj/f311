"""
VALD3-specific conversion
"""


import f311.filetypes as ft
import f311.physics as ph
import a99
from .calc_qgbd import calc_qgbd_tio_like
from .convlog import *
from collections import OrderedDict


__all__ = ["vald3_to_sols"]



def vald3_to_sols(molconsts, file_vald3, qgbd_calculator):
    """
    Converts HITRAN molecular lines data to PFANT "sets of lines"

    Args:
        molconsts: a dict-like object combining field values from tables 'molecule', 'state',
                    and 'pfantmol' from a FileMolDB database
        file_vald3: FileVald3 instance with only one species
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

    if not isinstance(file_vald3, ft.FileVald3):
        raise TypeError("Invalid type for argument 'file_vald3': {}".format(type(file_vald3)))
    if len(file_vald3) > 1:
        raise ValueError("Argument 'file_vald3' must have only one species, but it has {}".format(len(file_vald3)))

    lines = file_vald3.speciess[0].lines
    n = len(lines)

    S = molconsts.get_S2l()
    DELTAK = molconsts.get_deltak()

    sols = OrderedDict()  # one item per (vl, v2l) pair
    log = MolConversionLog(n)

    for i, line in enumerate(lines):
        assert isinstance(line, ft.Vald3Line)
        try:
            wl = line.lambda_
            # Br, J2l = f_group(data["local_lower_quanta"][i])
            # Jl = _Jl(Br, J2l)
            # V = f_class(data["global_upper_quanta"][i])
            # V_ = f_class(data["global_lower_quanta"][i])
            # A = data["a"][i]

            # A seguir normalizacion de factor de Honl-london (HLN)
            # TODO ask BLB: is this formula always like this?
            Normaliza = 1/((2.0*line.J2l+1)*(2.0*S+1)*(2.0-DELTAK))

            # A seguir teremos a forca de oscilador
            # mas q sera normalizada segundo o programa da Beatriz
            # gf = Normaliza*1.499*(2*Jl+1)*A/(nu**2)  <-- this was for HITRAN
            gf_pfant = Normaliza*10**line.loggf

            J2l_pfant = int(line.J2l)  # ojo, estamos colocando J2L-0.5! TODO ask BLB: we write J2l or J2l-.5?
        except Exception as e:
            log.errors.append("#{}{} line: {}".format(i+1, a99.ordinal_suffix(i+1), str(e)))
            continue

        sol_key = "%3d%3d" % (line.vl, line.v2l)  # (v', v'') transition (v_sup, v_inf)
        if sol_key not in sols:
            qgbd = qgbd_calculator(molconsts, line.v2l)
            qqv = qgbd["qv"]
            ggv = qgbd["gv"]
            bbv = qgbd["bv"]
            ddv = qgbd["dv"]
            sols[sol_key] = ft.SetOfLines(line.vl, line.v2l, qqv, ggv, bbv, ddv, 1.)

        sol = sols[sol_key]
        # TODO assuming singlet!!!
        sol.append_line(wl, gf_pfant, J2l_pfant, ph.singlet.quanta_to_branch(line.Jl, line.J2l))

    return (list(sols.values()), log)
