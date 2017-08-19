# TODO remake doublet
# TODO retrieve original comments
# TODO add reference U, C formulas come from 2.1.3-6
# TODO sort or add note for the "inverted terms" thing on page 126 (best if there is another example in Fortran )
# TODO test


"""
Hönl-London factors for doblets.

Only the case for Delta Lambda = +-1 implemented.
Formulas from Kovacs 1969 p136, p137, and formula 2.1.4-8

Original comments in Portuguese were quoted from ATMOS/wrk4/bruno/Mole/NH/sjnh.f

Routines in uppercase are adapted code from Fortran

- `YL`, `U*L` refer to the superior state
- `Y2l`, `U*2L` refer to the inferior state 

"""

from collections import OrderedDict
import a99
from . import honllondon_dict
import math


__all__ = ["honllondon", "quanta_to_branch"]



def quanta_to_branch(Jl, J2l, spinl=None, spin2l=None):
    """
    Converts quanta to branch

    Args:
        Jl: J upper or J'
        J2l: J lower or  J''
        spinl:
        spin2l: (cannot be None)

    Returns:
        str: if spinl is None or equals spin2l, (letter)(number),
             otherwise (letter)(number)(number)

    >>> quanta_to_branch(10.5, 11.5, spin2l=1)
    'P1'
    >>> quanta_to_branch(11.5, 10.5, spin2l=2)
    'R2'
    >>> quanta_to_branch(10.5, 10.5, spin2l=1)
    'Q1'

    """
    if Jl > J2l:
        br = "R"
    elif Jl == J2l:
        br =  "Q"
    else:
        br = "P"

    if spinl is None:
        ret = "{}{:1d}".format(br, spin2l)
    else:
        if spin2l is None:
          raise ValueError("spin2l cannot be None")

        if spinl == spin2l:
            ret = "{}{:1d}".format(br, spin2l)
        else:
            ret = "{}{:1d}{:1d}".format(br, spinl, spin2l)
    return ret


class honllondon(honllondon_dict):
    def _populate_with_key(self, key):
        vl, v2l, J, branch = key
        cc = self._mol_consts

        S = cc["s"]
        DELTAK = cc["cro"]
        FE = cc["fe"]
        LAML = cc["from_spdf"]
        LAM2L = cc["to_spdf"]

        # Original comment:
        #
        #     cada banda possue valores distintos de Y' e Y''
        #     quando Y=A/B > 0, temos o termo normal, por isso
        #     nao se modifica as formulas abaixo

        # TODO link these names in the documentation, gui_info, caption, description, whatever

        LAML = cc["from_spdf"]
        LAM2L = cc["to_spdf"]
        AL = cc["statel_A"]
        AEL = cc["statel_alpha_e"]
        BEL = cc["statel_B_e"]
        A2L = cc["state2l_A"]
        AE2L = cc["state2l_alpha_e"]
        BE2L = cc["state2l_B_e"]

        BL = BEL - AEL * (vl + 0.5)
        B2L = BE2L - AE2L * (v2l + 0.5)

        YL = AL / BL
        Y2L = A2L / B2L



        UPLUSL = lambda J: ((LAML**2.)*YL*(YL-4) + 4*((J+0.5)**2.))**0.5 + LAML*(YL-2) 
        UMINUSL= lambda J: ((LAML**2.)*YL*(YL-4) + 4*((J+0.5)**2.))**0.5 - LAML*(YL-2)
        CPLUSL = lambda J: 0.5*((UPLUSL(J)**2.) + 4*(((J+0.5)**2.) - LAML**2.))
        CMINUSL = lambda J: 0.5*((UMINUSL(J)**2.) + 4*(((J+0.5)**2.) - LAML**2.))
        UPLUS2L = lambda J: ((LAM2L**2.)*Y2L*(Y2L-4) + 4*((J+0.5)**2.))**0.5 + LAM2L*(Y2L-2)
        UMINUS2L = lambda J: ((LAM2L**2.)*Y2L*(Y2L-4) + 4*((J+0.5)**2.))**0.5 - LAM2L*(Y2L-2)
        CPLUS2L = lambda J: 0.5*((UPLUS2L(J)**2.) + 4*(((J+0.5)**2.)-LAM2L**2.))
        CMINUS2L = lambda J: 0.5*((UMINUS2L(J)**2.)+4*(((J+0.5)**2.)-LAM2L**2.)) 

        # Original comment:
        #
        #     usa-se o menor valor de Lambda nas formulas abaixo
        LMIN = min(LAML, LAM2L)

        _P1 = lambda J: \
            (((J-LMIN-1.5)*(J-LMIN-0.5))/(8*J*CMINUSL(J-1)*
            CMINUS2L(J)))*((UMINUSL(J-1)*UMINUS2L(J) +
            4*(J-LMIN+0.5)*(J+LMIN+0.5))**2.)

        _Q1 = lambda J: \
            (((J-LMIN-0.5)*(J+0.5)*(J+LMIN+1.5))/(4*J*(J+1)*
            CMINUSL(J)*CMINUS2L(J)))*((UMINUSL(J)*UMINUS2L(J) +
            4*(J-LMIN+0.5)*(J+LMIN+0.5))**2.)


        _R1 = lambda J: \
            (((J+LMIN+1.5)*(J+LMIN+2.5))/(8*(J+1)*CMINUSL(J+1)*
            CMINUS2L(J)))*((UMINUSL(J+1)*UMINUS2L(J) +
            4*(J-LMIN+0.5)*(J+LMIN+0.5))**2.)

        _P21 = lambda J: \
            (((J-LMIN-1.5)*(J-LMIN-0.5))/(8*J*CPLUSL(J-1)*
            CMINUS2L(J)))*((UPLUSL(J-1)*UMINUS2L(J) -
            4*(J-LMIN+0.5)*(J+LMIN+0.5))**2.)

        _Q21 = lambda J: \
            (((J-LMIN-0.5)*(J+0.5)*(J+LMIN+1.5))/(4*J*(J+1)*
            CPLUSL(J)*CMINUS2L(J)))*((UPLUSL(J)*UMINUS2L(J) -
            4*(J-LMIN+0.5)*(J+LMIN+0.5))**2.)


        _R21 = lambda J: \
            (((J+LMIN+1.5)*(J+LMIN+2.5))/(8*(J+1)*CPLUSL(J+1)*
            CMINUS2L(J)))*((UPLUSL(J+1)*UMINUS2L(J) -
            4*(J-LMIN+0.5)*(J+LMIN+0.5))**2.)


        _P12 = lambda J: \
            (((J-LMIN-1.5)*(J-LMIN-0.5))/
            (8*J*CMINUSL(J-1)*CPLUS2L(J)))*\
            ((UMINUSL(J-1)*UPLUS2L(J) - 4*(J-LMIN+0.5)*(J+LMIN+0.5))**2.)


        _Q12 = lambda J: \
            (((J-LMIN-0.5)*(J+0.5)*(J+LMIN+1.5))/(4*J*(J+1)*
            CMINUSL(J)*CPLUS2L(J)))*((UMINUSL(J)*UPLUS2L(J) -
            4*(J-LMIN+0.5)*(J+LMIN+0.5))**2.)


        _R12 = lambda J: \
            (((J+LMIN+1.5)*(J+LMIN+2.5))/(8*(J+1)*CMINUSL(J+1)*
            CPLUS2L(J)))*((UMINUSL(J+1)*UPLUS2L(J) -
            4*(J-LMIN+0.5)*(J+LMIN+0.5))**2.)


        _P2 = lambda J: \
            (((J-LMIN-1.5)*(J-LMIN-0.5))/(8*J*CPLUSL(J-1)*
            CPLUS2L(J)))*((UPLUSL(J-1)*UPLUS2L(J) +
            4*(J-LMIN+0.5)*(J+LMIN+0.5))**2.)


        _Q2 = lambda J: \
            (((J-LMIN-0.5)*(J+0.5)*(J+LMIN+1.5))/(4*J*(J+1)*
            CPLUSL(J)*CPLUS2L(J)))*((UPLUSL(J)*UPLUS2L(J) +
            4*(J-LMIN+0.5)*(J+LMIN+0.5))**2.)


        _R2 = lambda J: \
            (((J+LMIN+1.5)*(J+LMIN+2.5))/(8*(J+1)*CPLUSL(J+1)*
            CPLUS2L(J)))*((UPLUSL(J+1)*UPLUS2L(J) +
            4*(J-LMIN+0.5)*(J+LMIN+0.5))**2.)


        # Resolves the Delta Lambda

        if LAML > LAM2L:
            self.update(
                (
                    ("P1", _P1(J)),
                    ("Q1", _Q1(J)),
                    ("R1", _R1(J)),
                    ("P21", _P21(J)),
                    ("Q21", _Q21(J)),
                    ("R21", _R21(J)),
                    ("P12", _P12(J)),
                    ("Q12", _Q12(J)),
                    ("R12", _R12(J)),
                    ("P2", _P2(J)),
                    ("Q2", _Q2(J)),
                    ("R2", _R2(J)),
                ))

        elif LAML < LAM2L:
            self.update(
                (
                    ("P1", _R1(J-1)),
                    ("Q1", _Q1(J)),
                    ("R1", _P1(J+1)),
                    ("P21", _R12(J-1)),
                    ("Q21", _Q12(J)),
                    ("R21", _P12(J+1)),
                    ("P12", _R21(J-1)),
                    ("Q12", _Q21(J)),
                    ("R12", _P21(J+1)),
                    ("P2", _R2(J-1)),
                    ("Q2", _Q2(J)),
                    ("R2", _P2(J+1)),
                ))
