"""
Hönl-London factors for triplets.

Only the case for Delta Lambda = +-1 implemented.
Formulas from Kovacs 1969 p136, p137, and formula 2.1.4-8

Original comments in Portuguese were quoted from ATMOS/wrk4/bruno/Mole/NH/sjnh.f

Routines in uppercase are adapted code from Fortran

- `YL`, `U*L` refer to the superior state
- `Y2l`, `U*2L` refer to the inferior state 

"""

from collections import OrderedDict
import a99
from . import doublet
from . import honllondon_dict
import math


__all__ = ["honllondon", "quanta_to_branch"]


quanta_to_branch = doublet.quanta_to_branch


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

        # Original comment:
        #
        #     cálculo das contantes U1+, U1-, U3+, U3-,
        #     C1+, C2+, C3+, dependentes de J para o estado
        #     eletronico superior( A 3PI, lambda=1)
        #     formulas para casos intermediarios entre os casos A( Y>>J(J+1) )
        #     e B( Y<<J(J+1) ) de Hund
        #
        # Note: I (JT) changed some entity names for clarity and generality. For example:
        #
        #     - U1PLUSL was originally called U1MAA, ("MA" stood for "MAIS", "plus" in Portuguese;
        #       "A" stood the particular state for which the original NH code was developed and was replaced
        #       by "L", meaning "linha", to be consistent with a notation found in many places in the code)
        #     - "YL" was replaced by "YL", and "Y2L" was replaced by "Y2L" because, again, "L" and "2L"
        #       are used in other places to denote the superior and inferior levels, respectively

        U1PLUSL = lambda J: math.sqrt(LAML*LAML*YL*(YL-4)+4*J*J)+(LAML*(YL-2))
        U1MINUSL = lambda J: math.sqrt(LAML*LAML*YL*(YL-4)+4*J*J)-(LAML*(YL-2))
        U3PLUSL = lambda J: (LAML*LAML*YL*(YL-4)+4*(J+1)*(J+1))**.5+LAML*(YL-2)
        U3MINUSL = lambda J: ((LAML*LAML*YL*(YL-4)+4*(J+1)*(J+1))**0.5)-LAML*(YL-2)
        C1L = lambda J: LAML*LAML*YL*(YL-4)*(J-LAML+1)*(J+LAML)+2*(2*J+1)*(J-LAML)*(J+LAML)*J
        C2L = lambda J: LAML*LAML*YL*(YL-4)+4*J*(J+1)
        C3L = lambda J: LAML*LAML*YL*(YL-4)*(J-LAML)*(J+LAML+1)+2*(2*J+1)*(J-LAML+1)*(J+1)*(J+LAML+1)

        # Original comment:
        #
        #     idem para o estado eletronico inferior,
        #     X 3Sig( lambda=0)

        U1PLUS2L = lambda J: ((LAM2L*LAM2L*Y2L*(Y2L-4)+4*J*J))**.5+LAM2L*(Y2L-2)
        U1MINUS2L = lambda J: ((LAM2L*LAM2L*Y2L*(Y2L-4)+4*J*J))**.5-LAM2L*(Y2L-2)
        U3PLUS2L = lambda J: ((LAM2L*LAM2L*Y2L*(Y2L-4)+4*(J+1)*(J+1))**.5)+LAM2L*(Y2L-2)
        U3MINUS2L = lambda J: ((LAM2L*LAM2L*Y2L*(Y2L-4)+4*(J+1)*(J+1))**.5)-LAM2L*(Y2L-2)
        C12L = lambda J: LAM2L*LAM2L*Y2L*(Y2L-4)*(J-LAM2L+1)*(J+LAM2L)+2*(2*J+1)*(J-LAM2L)*J*(J+LAM2L)
        C22L = lambda J: LAM2L*LAM2L*Y2L*(Y2L-4)+4*J*(J+1)
        C32L = lambda J: LAM2L*LAM2L*Y2L*(Y2L-4)*(J-LAM2L)*(J+LAM2L+1)+2*(2*J+1)*(J-LAM2L+1)*(J+1)*(J+LAM2L+1)


        # Original comment:
        #
        #     usa-se o menor valor de Lambda nas formulas abaixo
        LMIN = min(LAML, LAM2L)


        _P1 = lambda J:\
            ((J-LMIN-1)*(J-LMIN))/(32*J*C1L(J-1)*C12L(J))* \
            (((J-LMIN+1)*(J+LMIN)*U1PLUSL(J-1)*U1PLUS2L(J)+
            (J-LMIN-2)*(J+LMIN+1)*U1MINUSL(J-1)*U1MINUS2L(J)+
            8*(J-LMIN-2)*(J-LMIN)*(J+LMIN)*(J+LMIN))**2)

        _Q1 = lambda J: \
            ((J-LMIN)*(J+LMIN+1)*(2*J+1))/(32*J*(J+1)*C1L(J)*C12L(J)) \
            *(((J-LMIN+1)*(J+LMIN)*U1PLUSL(J)*U1PLUS2L(J)+
            (J-LMIN-1)*(J+LMIN+2)*U1MINUSL(J)*U1MINUS2L(J)+
            8*(J-LMIN-1)*(J-LMIN)*(J+LMIN)*(J+LMIN+1))**2)

        _R1 = lambda J: \
            (((J+LMIN+1)*(J+LMIN+2))/(32*(J+1)*
            C1L(J+1)*C12L(J)))*(((J-LMIN+1)*(J+LMIN)*
            U1PLUSL(J+1)*U1PLUS2L(J)+(J-LMIN)*(J+LMIN+3)*U1MINUSL(J+1)*
            U1MINUS2L(J)+8*(J-LMIN)*(J-LMIN)*(J+LMIN)*(J+LMIN+2))**2)


        _P21 = lambda J: \
            (((J-LMIN-1)*(J-LMIN))/(4*J*C2L(J-1)*C12L(J)))* \
            (((J-LMIN+1)*(J+LMIN)*U1PLUS2L(J)-
            (J-LMIN-2)*(J+LMIN+1)*U1MINUS2L(J)-
            2*(LMIN+1)*(J-LMIN)*(J+LMIN)*(YL-2))**2)

        _Q21 = lambda J: \
            (((J-LMIN)*(J+LMIN+1)*(2*J+1))/(4*J*(J+1)*C2L(J)*C12L(J)))* \
            (((J-LMIN+1)*(J+LMIN)*U1PLUS2L(J)-
            (J-LMIN-1)*(J+LMIN+2)*U1MINUS2L(J)-
            2*(LMIN+1)*(J-LMIN)*(J+LMIN)*(YL-2))**2)

        _R21 = lambda J: \
            (((J+LMIN+1)*(J+LMIN+2))/(4*(J+1)*
            C2L(J+1)*C12L(J)))*(((J-LMIN+1)*(J+LMIN)*
            U1PLUS2L(J) - (J-LMIN)*(J+LMIN+3)*U1MINUS2L(J)
            - 2*(LMIN+1)*(J-LMIN)*(J+LMIN)*(YL-2))**2)

        _P31 = lambda J: \
            (((J-LMIN-1)*(J-LMIN))/(32*J*C3L(J-1)*C12L(J)))* \
            (((J-LMIN+1)*(J+LMIN)*U3MINUSL(J-1)*U1PLUS2L(J)+
            (J-LMIN-2)*(J+LMIN+1)*U3PLUSL(J-1)*U1MINUS2L(J)-
            8*(J-LMIN-1)*(J-LMIN)*(J+LMIN)*(J+LMIN+1))**2)

        _Q31 = lambda J: \
            (((J-LMIN)*(J+LMIN+1)*(2*J+1))/(32*J*(J+1)*C3L(J)*C12L(J))) \
            *(((J-LMIN+1)*(J+LMIN)*U3MINUSL(J)*U1PLUS2L(J)+
            (J-LMIN-1)*(J+LMIN+2)*U3PLUSL(J)*U1MINUS2L(J)-
            8*(J-LMIN)*(J-LMIN)*(J+LMIN)*(J+LMIN+2))**2)

        _R31 = lambda J: \
            (((J+LMIN+1)*(J+LMIN+2))/(32*(J+1)*
            C3L(J+1)*C12L(J)))*(((J-LMIN+1)*(J+LMIN)*
            U3MINUSL(J+1)*U1PLUS2L(J)+(J-LMIN)*(J+LMIN+3)*U3PLUSL(J+1)*
            U1MINUS2L(J)- 8*(J-LMIN)*(J-LMIN+1)*(J+LMIN)*(J+LMIN+3))**2)

        _P12 = lambda J: \
            (((J-LMIN-1)*(J-LMIN))/(4*J*C1L(J-1)*C22L(J)))* \
            (((J-LMIN+1)*(J+LMIN)*U1PLUSL(J-1)-
            (J-LMIN-2)*(J+LMIN+1)*U1MINUSL(J-1)-
            2*LMIN*(J-LMIN-2)*(J+LMIN)*(Y2L-2))**2)

        _Q12 = lambda J: \
            (((J-LMIN)*(J+LMIN+1)*(2*J+1))/(4*J*(J+1)*C1L(J)*C22L(J))) \
            *(((J-LMIN+1)*(J+LMIN)*U1PLUSL(J)-
            (J-LMIN-1)*(J+LMIN+2)*U1MINUSL(J)-
            2*LMIN*(J-LMIN-1)*(J+LMIN+1)*(Y2L-2))**2)

        _R12 = lambda J: \
            (((J+LMIN+1)*(J+LMIN+2))/(4*(J+1)*
            C1L(J+1)*C22L(J)))*(((J-LMIN+1)*(J+LMIN)*
            U1PLUSL(J+1) - (J-LMIN)*(J+LMIN+3)*U1MINUSL(J+1)
            - 2*LMIN*(J-LMIN)*(J+LMIN+2)*(Y2L-2))**2)

        _P2 = lambda J: \
            ((2*(J-LMIN-1)*(J-LMIN))/(J*C2L(J-1)*C22L(J)))* \
            ((.5*LMIN*(LMIN+1)*(YL-2)*(Y2L-2)+(J-LMIN+1)*(J+LMIN)+
            (J-LMIN-2)*(J+LMIN+1))**2)

        _Q2 = lambda J: \
            ((2*(J-LMIN)*(J+LMIN+1)*(2*J+1))/(J*(J+1)*C2L(J)*C22L(J)))* \
            ((.5*LMIN*(LMIN+1)*(YL-2)*(Y2L-2)+
            (J-LMIN+1)*(J+LMIN)+(J-LMIN-1)*(J+LMIN+2))**2)

        _R2 = lambda J: \
            ((2*(J+LMIN+1)*(J+LMIN+2))/((J+1)*
            C2L(J+1)*C22L(J)))*((.5*LMIN*(LMIN+1)*(YL-2)*(Y2L-2)+
            (J-LMIN+1)*(J+LMIN)+(J-LMIN)*(J+LMIN+3))**2)

        _P32 = lambda J: \
            (((J-LMIN-1)*(J-LMIN))/(4*J*C3L(J-1)*C22L(J)))* \
            (((J-LMIN+1)*(J+LMIN)*U3MINUSL(J-1)-
            (J-LMIN-2)*(J+LMIN+1)*U3PLUSL(J-1)+
            2*LMIN*(J-LMIN-1)*(J+LMIN+1)*(Y2L-2))**2)

        _Q32 = lambda J: \
            (((J-LMIN)*(J+LMIN+1)*(2*J+1))/(4*J*(J+1)*C3L(J)*C22L(J))) \
            *(((J-LMIN+1)*(J+LMIN)*U3MINUSL(J)-
            (J-LMIN-1)*(J+LMIN+2)*U3PLUSL(J)+
            2*LMIN*(J-LMIN)*(J+LMIN+2)*(Y2L-2))**2)

        _R32 = lambda J: \
            (((J+LMIN+1)*(J+LMIN+2))/(4*(J+1)*
            C3L(J+1)*C22L(J)))*(((J-LMIN+1)*(J+LMIN)*
            U3MINUSL(J+1) - (J-LMIN)*(J+LMIN+3)*U3PLUSL(J+1)
            + 2*LMIN*(J-LMIN+1)*(J+LMIN+3)*(Y2L-2))**2)

        _P13 = lambda J: \
            (((J-LMIN-1)*(J-LMIN))/(32*J*C1L(J-1)*
            C32L(J)))*(((J-LMIN+1)*(J+LMIN)*U1PLUSL(J-1)*
            U3MINUS2L(J)+ (J-LMIN-2)*(J+LMIN+1)*U1MINUSL(J-1)*U3PLUS2L(J)-
            8*(J-LMIN-2)*(J-LMIN+1)*(J+LMIN)*(J+LMIN+1))**2)

        _Q13 = lambda J: \
            (((J-LMIN)*(J+LMIN+1)*(2*J+1))/(32*J*(J+1)*C1L(J)*C32L(J)))* \
            (((J-LMIN+1)*(J+LMIN)*U1PLUSL(J)*U3MINUS2L(J)+
            (J-LMIN-1)*(J+LMIN+2)*U1MINUSL(J)*U3PLUS2L(J)-
            8*(J-LMIN-1)*(J-LMIN+1)*(J+LMIN+1)*(J+LMIN+1))**2)

        _R13 = lambda J: \
            (((J+LMIN+1)*(J+LMIN+2))/(32*(J+1)*
            C1L(J+1)*C32L(J)))*(((J-LMIN+1)*(J+LMIN)*U1PLUSL(J+1)
            *U3MINUS2L(J)+(J-LMIN)*(J+LMIN+3)*U1MINUSL(J+1)*U3PLUS2L(J)-
            8*(J-LMIN)*(J-LMIN+1)*(J+LMIN+1)*(J+LMIN+2))**2)

        _P23 = lambda J: \
            (((J-LMIN-1)*(J-LMIN))/(4*J*C2L(J-1)*C32L(J)))* \
            (((J-LMIN+1)*(J+LMIN)*U3MINUS2L(J)-
            (J-LMIN-2)*(J+LMIN+1)*U3PLUS2L(J)+
            2*(LMIN+1)*(J-LMIN+1)*(J+LMIN+1)*(YL-2))**2)

        _Q23 = lambda J: \
            (((J-LMIN)*(J+LMIN+1)*(2*J+1))/(4*J*(J+1)*C2L(J)*C32L(J))) \
            *(((J-LMIN+1)*(J+LMIN)*U3MINUS2L(J)-
            (J-LMIN-1)*(J+LMIN+2)*U3PLUS2L(J)+
            2*(LMIN+1)*(J-LMIN+1)*(J+LMIN+1)*(YL-2))**2)

        _R23 = lambda J: \
            (((J+LMIN+1)*(J+LMIN+2))/(4*(J+1)*
            C2L(J+1)*C32L(J)))*(((J-LMIN+1)*(J+LMIN)*
            U3MINUS2L(J) - (J-LMIN)*(J+LMIN+3)*U3PLUS2L(J)
            + 2*(LMIN+1)*(J-LMIN+1)*(J+LMIN+1)*(YL-2))**2)

        _P3 = lambda J: \
            (((J-LMIN-1)*(J-LMIN))/(32*J*C3L(J-1)*
            C32L(J)))*(((J-LMIN+1)*(J+LMIN)*U3MINUSL(J-1)*
            U3MINUS2L(J)+(J-LMIN-2)*(J+LMIN+1)*U3PLUSL(J-1)*U3PLUS2L(J)+
            8*(J-LMIN-1)*(J-LMIN+1)*(J+LMIN+1)*(J+LMIN+1))**2)

        _Q3 = lambda J: \
            (((J-LMIN)*(J+LMIN+1)*(2*J+1))/(32*J*(J+1)*C3L(J)*C32L(J)))* \
            (((J-LMIN+1)*(J+LMIN)*U3MINUSL(J)*U3MINUS2L(J)+
            (J-LMIN-1)*(J+LMIN+2)*U3PLUSL(J)*U3PLUS2L(J)+
            8*(J-LMIN)*(J-LMIN+1)*(J+LMIN+1)*(J+LMIN+2))**2)

        _R3 = lambda J: \
            (((J+LMIN+1)*(J+LMIN+2))/(32*(J+1)*
            C3L(J+1)*C32L(J)))*(((J-LMIN+1)*(J+LMIN)*U3MINUSL(J+1)
            *U3MINUS2L(J)+(J-LMIN)*(J+LMIN+3)*U3PLUSL(J+1)*U3PLUS2L(J)+
            8*(J-LMIN+1)*(J-LMIN+1)*(J+LMIN+1)*(J+LMIN+3))**2)

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
                    ("P31", _P31(J)),
                    ("Q31", _Q31(J)),
                    ("R31", _R31(J)),
                    ("P12", _P12(J)),
                    ("Q12", _Q12(J)),
                    ("R12", _R12(J)),
                    ("P2", _P2(J)),
                    ("Q2", _Q2(J)),
                    ("R2", _R2(J)),
                    ("P32", _P32(J)),
                    ("Q32", _Q32(J)),
                    ("R32", _R32(J)),
                    ("P13", _P13(J)),
                    ("Q13", _Q13(J)),
                    ("R13", _R13(J)),
                    ("P23", _P23(J)),
                    ("Q23", _Q23(J)),
                    ("R23", _R23(J)),
                    ("P3", _P3(J)),
                    ("Q3", _Q3(J)),
                    ("R3", _R3(J)),
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
                    ("P31", _R13(J-1)),
                    ("Q31", _Q13(J)),
                    ("R31", _P13(J+1)),
                    ("P12", _R21(J-1)),
                    ("Q12", _Q21(J)),
                    ("R12", _P21(J+1)),
                    ("P2", _R2(J-1)),
                    ("Q2", _Q2(J)),
                    ("R2", _P2(J+1)),
                    ("P32", _R23(J-1)),
                    ("Q32", _Q23(J)),
                    ("R32", _P23(J+1)),
                    ("P13", _R31(J-1)),
                    ("Q13", _Q31(J)),
                    ("R13", _P31(J+1)),
                    ("P23", _R32(J-1)),
                    ("Q23", _Q32(J)),
                    ("R23", _P32(J+1)),
                    ("P3", _R3(J-1)),
                    ("Q3", _Q3(J)),
                    ("R3", _P3(J+1)),
                ))

            # Adds keys to dictionary


# NEXT: RESOLVE THE DELTA_LAMBDA AND STUFF THE OBJECT



# TODO cleanup
    # Original comment:
    #
    #     cálculo das contantes U1+, U1-, U3+, U3-,
    #     C1+, C2+, C3+, dependentes de J para o estado
    #     eletronico superior( A 3PI, lambda=1)
    #     formulas para casos intermediarios entre os casos A( Y>>J(J+1) )
    #     e B( Y<<J(J+1) ) de Hund
    #
    # Note: I (JT) changed some entity names for clarity and generality. For example:
    #
    #     - U1PLUSL was originally called U1MAA, ("MA" stood for "MAIS", "plus" in Portuguese;
    #       "A" stood the particular state for which the original NH code was developed and was replaced
    #       by "L", meaning "linha", to be consistent with a notation found in many places in the code)
    #     - "YL" was replaced by "YL", and "Y2L" was replaced by "Y2L" because, again, "L" and "2L"
    #       are used in other places to denote the superior and inferior levels, respectively

    # def U1PLUSL(J, LAML, YL):
    #    return math.sqrt(LAML*LAML*YL*(YL-4)+4*J*J)+(LAML*(YL-2))
    #
    # def U1MINUSL(J, LAML, YL):
    #     return math.sqrt(LAML*LAML*YL*(YL-4)+4*J*J)-(LAML*(YL-2))
    #
    # def U3PLUSL(J, LAML, YL):
    #     return (LAML*LAML*YL*(YL-4)+4*(J+1)*(J+1))**.5+LAML*(YL-2)
    #
    # def U3MINUSL(J, LAML, YL):
    #     return ((LAML*LAML*YL*(YL-4)+4*(J+1)*(J+1))**0.5)-LAML*(YL-2)
    #
    # def C1L(J, LAML, YL):
    #     return LAML*LAML*YL*(YL-4)*(J-LAML+1)*(J+LAML)+2*(2*J+1)*(J-LAML)*(J+LAML)*J
    #
    # def C2L(J, LAML, YL):
    #     return LAML*LAML*YL*(YL-4)+4*J*(J+1)
    #
    # def C3L(J, LAML, YL):
    #     return LAML*LAML*YL*(YL-4)*(J-LAML)*(J+LAML+1)+2*(2*J+1)*(J-LAML+1)*(J+1)*(J+LAML+1)
    #
    # # Original comment:
    # #
    # #     idem para o estado eletronico inferior,
    # #     X 3Sig( lambda=0)
    #
    # def U1PLUS2L(J, LAM2L, Y2L):
    #     return ((LAM2L*LAM2L*Y2L*(Y2L-4)+4*J*J))**.5+LAM2L*(Y2L-2)
    #
    # def U1MINUS2L(J, LAM2L, Y2L):
    #     return ((LAM2L*LAM2L*Y2L*(Y2L-4)+4*J*J))**.5-LAM2L*(Y2L-2)
    #
    # def U3PLUS2L(J, LAM2L, Y2L):
    #     return ((LAM2L*LAM2L*Y2L*(Y2L-4)+4*(J+1)*(J+1))**.5)+LAM2L*(Y2L-2)
    #
    # def U3MINUS2L(J, LAM2L, Y2L):
    #     return ((LAM2L*LAM2L*Y2L*(Y2L-4)+4*(J+1)*(J+1))**.5)-LAM2L*(Y2L-2)
    #
    # def C12L(J, LAM2L, Y2L):
    #     return LAM2L*LAM2L*Y2L*(Y2L-4)*(J-LAM2L+1)*(J+LAM2L)+2*(2*J+1)*(J-LAM2L)*J*(J+LAM2L)
    #
    # def C22L(J, LAM2L, Y2L):
    #     return LAM2L*LAM2L*Y2L*(Y2L-4)+4*J*(J+1)
    #
    # def C32L(J, LAM2L, Y2L):
    #     return LAM2L*LAM2L*Y2L*(Y2L-4)*(J-LAM2L)*(J+LAM2L+1)+2*(2*J+1)*(J-LAM2L+1)*(J+1)*(J+LAM2L+1)


# P1
# Q1
# R1
# P21
# Q21
# R21
# P31
# Q31
# R31
# P12
# Q12
# R12
# P2
# Q2
# R2
# P32
# Q32
# R32
# P13
# Q13
# R13
# P23
# Q23
# R23
# P3
# Q3
# R3


(
("P1", _P1),
("Q1", _Q1),
("R1", _R1),
("P21", _P21),
("Q21", _Q21),
("R21", _R21),
("P31", _P31),
("Q31", _Q31),
("R31", _R31),
("P12", _P12),
("Q12", _Q12),
("R12", _R12),
("P2", _P2),
("Q2", _Q2),
("R2", _R2),
("P32", _P32),
("Q32", _Q32),
("R32", _R32),
("P13", _P13),
("Q13", _Q13),
("R13", _R13),
("P23", _P23),
("Q23", _Q23),
("R23", _R23),
("P3", _P3),
("Q3", _Q3),
("R3", _R3),
)