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
from . import honllondon_defaultdict
import math


__all__ = ["honllondon", "quanta_to_branch"]


quanta_to_branch = doublet.quanta_to_branch




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
#     - "YLI" was replaced by "YL", and "Y2LI" was replaced by "Y2L" because, again, "L" and "2L"
#       are used in other places to denote the superior and inferior levels, respectively

def U1PLUSL(J, LAML, YL):
   return math.sqrt(LAML*LAML*YL*(YL-4)+4*J*J)+(LAML*(YL-2))

def U1MEA(J, LAML, YL):
    return math.sqrt(LAML*LAML*YL*(YL-4)+4*J*J)-(LAML*(YL-2))

def U3PLUSL(J, LAML, YL):
    return (LAML*LAML*YL*(YL-4)+4*(J+1)*(J+1))**.5+LAML*(YL-2)

def U3MINUSL(J, LAML, YL):
    return ((LAML*LAML*YL*(YL-4)+4*(J+1)*(J+1))**0.5)-LAML*(YL-2)
    
def C1L(J, LAML, YL):
    return LAML*LAML*YL*(YL-4)*(J-LAML+1)*(J+LAML)+2*(2*J+1)*(J-LAML)*(J+LAML)*J

def C2L(J, LAML, YL):
    return LAML*LAML*YL*(YL-4)+4*J*(J+1)

def C3L(J, LAML, YL):
    return LAML*LAML*YL*(YL-4)*(J-LAML)*(J+LAML+1)+2*(2*J+1)*(J-LAML+1)*(J+1)*(J+LAML+1)

# Original comment:
#
#     idem para o estado eletronico inferior,
#     X 3Sig( lambda=0)

def U1PLUS2L(J, LAM2L, Y2L):
    return ((LAM2L*LAM2L*Y2L*(Y2L-4)+4*J*J))**.5+LAM2L*(Y2L-2)
    
def U1MINUS2L(J, LAM2L, Y2L):
    return ((LAM2L*LAM2L*Y2L*(Y2L-4)+4*J*J))**.5-LAM2L*(Y2L-2)
    
def U3PLUS2L(J, LAM2L, Y2L):
    return ((LAM2L*LAM2L*Y2L*(Y2L-4)+4*(J+1)*(J+1))**.5)+LAM2L*(Y2L-2)
    
def U3MINUS2L(J, LAM2L, Y2L):
    return ((LAM2L*LAM2L*Y2L*(Y2L-4)+4*(J+1)*(J+1))**.5)-LAM2L*(Y2L-2)
    
def C12L(J, LAM2L, Y2L):
    return LAM2L*LAM2L*Y2L*(Y2L-4)*(J-LAM2L+1)*(J+LAM2L)+2*(2*J+1)*(J-LAM2L)*J*(J+LAM2L)
    
def C22L(J, LAM2L, Y2L):
    return LAM2L*LAM2L*Y2L*(Y2L-4)+4*J*(J+1)
    
def C32L(J, LAM2L, Y2L):
    return LAM2L*LAM2L*Y2L*(Y2L-4)*(J-LAM2L)*(J+LAM2L+1)+2*(2*J+1)*(J-LAM2L+1)*(J+1)*(J+LAM2L+1)











# TODO make mol_consts standard and put this documentation somewhere (where)?

def _new_honllondon(key, mol_consts):
    """

    Args:
        key: (vl, v2l, J)
        mol_consts: dictionary with keys TODO

    Returns:
        float: Hönl-London factor
    """
    S = mol_consts["s"]
    DELTAK = mol_consts["cro"]
    FE = mol_consts["fe"]
    LAML = mol_consts["from_spdf"]
    LAM2L = mol_consts["to_spdf"]

    # Original comment:
    #
    #     cada banda possue valores distintos de Y' e Y''
    #     quando Y=A/B > 0, temos o termo normal, por isso
    #     nao se modifica as formulas abaixo


    AL = -34.7
    BEL = 16.6745
    AEL = 0.7454
    BL = BEL - AEL * (VL(T) + 0.5)

    A2L = 0.0
    BE2L = 16.6993
    AE2L = 0.6490
    B2L = BE2L - AE2L * (V2L(T) + 0.5)

"""

       AL = -34.7
       BEL = 16.6745
       AEL= 0.7454
       BL= BEL - AEL*(VL(T)+0.5)

       A2L = 0.0
       BE2L = 16.6993
       AE2L = 0.6490
       B2L= BE2L - AE2L*(V2L(T)+0.5)

       YLI = AL/BL
       Y2LI = A2L/B2L

C      ca'lculo das contantes U1+, U1-, U3+, U3-,
C      C1+, C2+, C3+, dependentes de J para o estado
C      eletronico superior( A 3PI, lambda=1)
C      formulas para casos intermediarios entre os casos A( Y>>J(J+1) )
C      e B( Y<<J(J+1) ) de Hund
       DO 1 J=3,JTOT
       LAM=1
def U1PLUSL(J, LAML, YL):
    return math.sqrt(LAM*LAM*YLI*(YLI-4)+4*J*J)+
     1 (LAM*(YLI-2)))
def U1MINUSL(J, LAML, YL):
    return math.sqrt(LAM*LAM*YLI*(YLI-4)+4*J*J)-
     1 (LAM*(YLI-2)))
def U3PLUSL(J, LAML, YL):
    return (LAM*LAM*YLI*(YLI-4)+4*(J+1)*(J+1))
     1  **.5+LAM*(YLI-2))
def U3MINUSL(J, LAML, YL):
    return ((LAM*LAM*YLI*(YLI-4)+4*(J+1)*(J+1))
     1 **0.5)-LAM*(YLI-2))
def C1L(J, LAML, YL):
    return LAM*LAM*YLI*(YLI-4)*(J-LAM+1)*(J+LAM)+
     1 2*(2*J+1)*(J-LAM)*(J+LAM)*J)
def C2L(J, LAML, YL):
    return LAM*LAM*YLI*(YLI-4)+4*J*(J+1))
def C3L(J, LAML, YL):
    return LAM*LAM*YLI*(YLI-4)*(J-LAM)*(J+LAM+1)+
     1 2*(2*J+1)*(J-LAM+1)*(J+1)*(J+LAM+1))
    1  CONTINUE

C      idem para o estado eletronico inferior,
C      X 3Sig( lambda=0)
       DO 2 J=3,JTOT
       LAM=0
def U1PLUS2L(J, LAML, YL):
    return ((LAM*LAM*Y2LI*(Y2LI-4)+4*J*J))**.5+
     1 LAM*(Y2LI-2))
def U1MINUS2L(J, LAML, YL):
    return ((LAM*LAM*Y2LI*(Y2LI-4)+4*J*J))**.5-
     1 LAM*(Y2LI-2))
def U3PLUS2L(J, LAML, YL):
    return ((LAM*LAM*Y2LI*(Y2LI-4)+4*(J+1)*(J+1))
     1 **.5)+LAM*(Y2LI-2))
def U3MINUS2L(J, LAML, YL):
    return ((LAM*LAM*Y2LI*(Y2LI-4)+4*(J+1)*
     1 (J+1))**.5)-LAM*(Y2LI-2))
def C12L(J, LAML, YL):
    return LAM*LAM*Y2LI*(Y2LI-4)*(J-LAM+1)*(J+LAM)+
     1 2*(2*J+1)*(J-LAM)*J*(J+LAM))
def C22L(J, LAML, YL):
    return LAM*LAM*Y2LI*(Y2LI-4)+4*J*(J+1))
def C32L(J, LAML, YL):
    return LAM*LAM*Y2LI*(Y2LI-4)*(J-LAM)*(J+LAM+1)+
     1 2*(2*J+1)*(J-LAM+1)*(J+1)*(J+LAM+1))
    2  CONTINUE

C      calculo das forcas das linha, S(J''), "fatores Honl-London",
C      para os 3 ramos principais,
C      P(J), J' - J''= +1
C      Q(J), delta J=0 e
C      R(J), J' - J''= -1
C      subdividos em tres, "transicao tripleto"
C      os 18 subramos satelites podem ser desprezados por apresentarem
C      linhas de intensidade fraca e nao-identificadas pela literatura

       DO 10 J=4,KTOT
C      usa-se o menor valor de Lambda nas formulas abaixo
       LAM=0
def P1(J, LAML, YL):
    return ((J-LAM-1)*(J-LAM))/(32*J*C1L(J-1)*C12L(J)))*
     1 (((J-LAM+1)*(J+LAM)*U1PLUSL(J-1)*U1PLUS2L(J)+
     2  (J-LAM-2)*(J+LAM+1)*U1MINUSL(J-1)*U1MINUS2L(J)+
     3  8*(J-LAM-2)*(J-LAM)*(J+LAM)*(J+LAM))**2)
def Q1(J, LAML, YL):
    return ((J-LAM)*(J+LAM+1)*(2*J+1))/(32*J*(J+1)*C1L(J)*C12L(J)))
     1 *(((J-LAM+1)*(J+LAM)*U1PLUSL(J)*U1PLUS2L(J)+
     2 (J-LAM-1)*(J+LAM+2)*U1MINUSL(J)*U1MINUS2L(J)+
     3 8*(J-LAM-1)*(J-LAM)*(J+LAM)*(J+LAM+1))**2)
def R1(J, LAML, YL):
    return ((J+LAM+1)*(J+LAM+2))/(32*(J+1)*
     1 C1L(J+1)*C12L(J)))*(((J-LAM+1)*(J+LAM)*
     2 U1PLUSL(J+1)*U1PLUS2L(J)+(J-LAM)*(J+LAM+3)*U1MINUSL(J+1)*
     3 U1MINUS2L(J)+8*(J-LAM)*(J-LAM)*(J+LAM)*(J+LAM+2))**2)
def P21(J, LAML, YL):
    return ((J-LAM-1)*(J-LAM))/(4*J*C2L(J-1)*C12L(J)))*
     1 (((J-LAM+1)*(J+LAM)*U1PLUS2L(J)-
     2  (J-LAM-2)*(J+LAM+1)*U1MINUS2L(J)-
     3  2*(LAM+1)*(J-LAM)*(J+LAM)*(YLI-2))**2)
def Q21(J, LAML, YL):
    return ((J-LAM)*(J+LAM+1)*(2*J+1))/(4*J*(J+1)*C2L(J)*C12L(J)))
     1 *(((J-LAM+1)*(J+LAM)*U1PLUS2L(J)-
     2 (J-LAM-1)*(J+LAM+2)*U1MINUS2L(J)-
     3 2*(LAM+1)*(J-LAM)*(J+LAM)*(YLI-2))**2)
def R21(J, LAML, YL):
    return ((J+LAM+1)*(J+LAM+2))/(4*(J+1)*
     1 C2L(J+1)*C12L(J)))*(((J-LAM+1)*(J+LAM)*
     2 U1PLUS2L(J) - (J-LAM)*(J+LAM+3)*U1MINUS2L(J)
     3 - 2*(LAM+1)*(J-LAM)*(J+LAM)*(YLI-2))**2)
def P31(J, LAML, YL):
    return ((J-LAM-1)*(J-LAM))/(32*J*C3L(J-1)*C12L(J)))*
     1 (((J-LAM+1)*(J+LAM)*U3MINUSL(J-1)*U1PLUS2L(J)+
     2  (J-LAM-2)*(J+LAM+1)*U3PLUSL(J-1)*U1MINUS2L(J)-
     3  8*(J-LAM-1)*(J-LAM)*(J+LAM)*(J+LAM+1))**2)
def Q31(J, LAML, YL):
    return ((J-LAM)*(J+LAM+1)*(2*J+1))/(32*J*(J+1)*C3L(J)*C12L(J)))
     1 *(((J-LAM+1)*(J+LAM)*U3MINUSL(J)*U1PLUS2L(J)+
     2 (J-LAM-1)*(J+LAM+2)*U3PLUSL(J)*U1MINUS2L(J)-
     3 8*(J-LAM)*(J-LAM)*(J+LAM)*(J+LAM+2))**2)
def R31(J, LAML, YL):
    return ((J+LAM+1)*(J+LAM+2))/(32*(J+1)*
     1 C3L(J+1)*C12L(J)))*(((J-LAM+1)*(J+LAM)*
     2 U3MINUSL(J+1)*U1PLUS2L(J)+(J-LAM)*(J+LAM+3)*U3PLUSL(J+1)*
     3 U1MINUS2L(J)- 8*(J-LAM)*(J-LAM+1)*(J+LAM)*(J+LAM+3))**2)
def P12(J, LAML, YL):
    return ((J-LAM-1)*(J-LAM))/(4*J*C1L(J-1)*C22L(J)))*
     1 (((J-LAM+1)*(J+LAM)*U1PLUSL(J-1)-
     2  (J-LAM-2)*(J+LAM+1)*U1MINUSL(J-1)-
     3  2*LAM*(J-LAM-2)*(J+LAM)*(Y2LI-2))**2)
def Q12(J, LAML, YL):
    return ((J-LAM)*(J+LAM+1)*(2*J+1))/(4*J*(J+1)*C1L(J)*C22L(J)))
     1 *(((J-LAM+1)*(J+LAM)*U1PLUSL(J)-
     2 (J-LAM-1)*(J+LAM+2)*U1MINUSL(J)-
     3 2*LAM*(J-LAM-1)*(J+LAM+1)*(Y2LI-2))**2)
def R12(J, LAML, YL):
    return ((J+LAM+1)*(J+LAM+2))/(4*(J+1)*
     1 C1L(J+1)*C22L(J)))*(((J-LAM+1)*(J+LAM)*
     2 U1PLUSL(J+1) - (J-LAM)*(J+LAM+3)*U1MINUSL(J+1)
     3 - 2*LAM*(J-LAM)*(J+LAM+2)*(Y2LI-2))**2)
def P2(J, LAML, YL):
    return (2*(J-LAM-1)*(J-LAM))/(J*C2L(J-1)*C22L(J)))*
     1 ((.5*LAM*(LAM+1)*(YLI-2)*(Y2LI-2)+(J-LAM+1)*(J+LAM)+
     2 (J-LAM-2)*(J+LAM+1))**2)
def Q2(J, LAML, YL):
    return (2*(J-LAM)*(J+LAM+1)*(2*J+1))/(J*(J+1)*C2L(J)*C22L(J)))*
     1 ((.5*LAM*(LAM+1)*(YLI-2)*(Y2LI-2)+
     2 (J-LAM+1)*(J+LAM)+(J-LAM-1)*(J+LAM+2))**2)
def R2(J, LAML, YL):
    return (2*(J+LAM+1)*(J+LAM+2))/((J+1)*
     1 C2L(J+1)*C22L(J)))*((.5*LAM*(LAM+1)*(YLI-2)*(Y2LI-2)+
     2 (J-LAM+1)*(J+LAM)+(J-LAM)*(J+LAM+3))**2)
def P32(J, LAML, YL):
    return ((J-LAM-1)*(J-LAM))/(4*J*C3L(J-1)*C22L(J)))*
     1 (((J-LAM+1)*(J+LAM)*U3MINUSL(J-1)-
     2  (J-LAM-2)*(J+LAM+1)*U3PLUSL(J-1)+
     3  2*LAM*(J-LAM-1)*(J+LAM+1)*(Y2LI-2))**2)
def Q32(J, LAML, YL):
    return ((J-LAM)*(J+LAM+1)*(2*J+1))/(4*J*(J+1)*C3L(J)*C22L(J)))
     1 *(((J-LAM+1)*(J+LAM)*U3MINUSL(J)-
     2 (J-LAM-1)*(J+LAM+2)*U3PLUSL(J)+
     3 2*LAM*(J-LAM)*(J+LAM+2)*(Y2LI-2))**2)
def R32(J, LAML, YL):
    return ((J+LAM+1)*(J+LAM+2))/(4*(J+1)*
     1 C3L(J+1)*C22L(J)))*(((J-LAM+1)*(J+LAM)*
     2 U3MINUSL(J+1) - (J-LAM)*(J+LAM+3)*U3PLUSL(J+1)
     3 + 2*LAM*(J-LAM+1)*(J+LAM+3)*(Y2LI-2))**2)
def P13(J, LAML, YL):
    return ((J-LAM-1)*(J-LAM))/(32*J*C1L(J-1)*
     1 C32L(J)))*(((J-LAM+1)*(J+LAM)*U1PLUSL(J-1)*
     2 U3MINUS2L(J)+ (J-LAM-2)*(J+LAM+1)*U1MINUSL(J-1)*U3PLUS2L(J)-
     3 8*(J-LAM-2)*(J-LAM+1)*(J+LAM)*(J+LAM+1))**2)
def Q13(J, LAML, YL):
    return ((J-LAM)*(J+LAM+1)*(2*J+1))/(32*J*(J+1)*C1L(J)*C32L(J)))*
     1 (((J-LAM+1)*(J+LAM)*U1PLUSL(J)*U3MINUS2L(J)+
     2 (J-LAM-1)*(J+LAM+2)*U1MINUSL(J)*U3PLUS2L(J)-
     3 8*(J-LAM-1)*(J-LAM+1)*(J+LAM+1)*(J+LAM+1))**2)
def R13(J, LAML, YL):
    return ((J+LAM+1)*(J+LAM+2))/(32*(J+1)*
     1 C1L(J+1)*C32L(J)))*(((J-LAM+1)*(J+LAM)*U1PLUSL(J+1)
     2 *U3MINUS2L(J)+(J-LAM)*(J+LAM+3)*U1MINUSL(J+1)*U3PLUS2L(J)-
     3 8*(J-LAM)*(J-LAM+1)*(J+LAM+1)*(J+LAM+2))**2)
def P23(J, LAML, YL):
    return ((J-LAM-1)*(J-LAM))/(4*J*C2L(J-1)*C32L(J)))*
     1 (((J-LAM+1)*(J+LAM)*U3MINUS2L(J)-
     2  (J-LAM-2)*(J+LAM+1)*U3PLUS2L(J)+
     3  2*(LAM+1)*(J-LAM+1)*(J+LAM+1)*(YLI-2))**2)
def Q23(J, LAML, YL):
    return ((J-LAM)*(J+LAM+1)*(2*J+1))/(4*J*(J+1)*C2L(J)*C32L(J)))
     1 *(((J-LAM+1)*(J+LAM)*U3MINUS2L(J)-
     2 (J-LAM-1)*(J+LAM+2)*U3PLUS2L(J)+
     3 2*(LAM+1)*(J-LAM+1)*(J+LAM+1)*(YLI-2))**2)
def R23(J, LAML, YL):
    return ((J+LAM+1)*(J+LAM+2))/(4*(J+1)*
     1 C2L(J+1)*C32L(J)))*(((J-LAM+1)*(J+LAM)*
     2 U3MINUS2L(J) - (J-LAM)*(J+LAM+3)*U3PLUS2L(J)
     3 + 2*(LAM+1)*(J-LAM+1)*(J+LAM+1)*(YLI-2))**2)
def P3(J, LAML, YL):
    return ((J-LAM-1)*(J-LAM))/(32*J*C3L(J-1)*
     1 C32L(J)))*(((J-LAM+1)*(J+LAM)*U3MINUSL(J-1)*
     2 U3MINUS2L(J)+(J-LAM-2)*(J+LAM+1)*U3PLUSL(J-1)*U3PLUS2L(J)+
     3 8*(J-LAM-1)*(J-LAM+1)*(J+LAM+1)*(J+LAM+1))**2)
def Q3(J, LAML, YL):
    return ((J-LAM)*(J+LAM+1)*(2*J+1))/(32*J*(J+1)*C3L(J)*C32L(J)))*
     1 (((J-LAM+1)*(J+LAM)*U3MINUSL(J)*U3MINUS2L(J)+
     2 (J-LAM-1)*(J+LAM+2)*U3PLUSL(J)*U3PLUS2L(J)+
     3 8*(J-LAM)*(J-LAM+1)*(J+LAM+1)*(J+LAM+2))**2)
def R3(J, LAML, YL):
    return ((J+LAM+1)*(J+LAM+2))/(32*(J+1)*
     1 C3L(J+1)*C32L(J)))*(((J-LAM+1)*(J+LAM)*U3MINUSL(J+1)
     2 *U3MINUS2L(J)+(J-LAM)*(J+LAM+3)*U3PLUSL(J+1)*U3PLUS2L(J)+
     3 8*(J-LAM+1)*(J-LAM+1)*(J+LAM+1)*(J+LAM+3))**2)

C     aqui FAZ-se a normalizacao dos fatores Honl-London:
C     o somatorio de S(J'') para um dado J'' deve ser igual a
C     (2J''+1)*(2-delat de Cron.)*(2S+1)
C     aqui, (2S+1)= 3 e delta de Cron.=0
C     entao, Soma( S(J)N/(2J+1)(2S+1)(2-DELTA), J fixo) = 1 !!!
C     a multiplicacao pelo fator 2, logo abaixo, representa isto.
C     os verdadeiros fatores rotacionais(H-London) sao o dobro das
C     formulas de Kovacs(1969) acima
       P1(J)=2*P1(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       P2(J)=2*P2(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       P3(J)=2*P3(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       P21(J)=2*P21(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       P31(J)=2*P31(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       P12(J)=2*P12(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       P32(J)=2*P32(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       P13(J)=2*P13(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       P23(J)=2*P23(J)/((2*J+1)*(2*S+1)*(2-DELTAK))

       R1(J)=2*R1(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       R2(J)=2*R2(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       R3(J)=2*R3(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       R21(J)=2*R21(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       R31(J)=2*R31(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       R12(J)=2*R12(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       R32(J)=2*R32(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       R13(J)=2*R13(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       R23(J)=2*R23(J)/((2*J+1)*(2*S+1)*(2-DELTAK))

       Q1(J)=2*Q1(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       Q2(J)=2*Q2(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       Q3(J)=2*Q3(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       Q21(J)=2*Q21(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       Q31(J)=2*Q31(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       Q12(J)=2*Q12(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       Q32(J)=2*Q32(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       Q13(J)=2*Q13(J)/((2*J+1)*(2*S+1)*(2-DELTAK))
       Q23(J)=2*Q23(J)/((2*J+1)*(2*S+1)*(2-DELTAK))

       SUM(J)=P1(J)+P2(J)+P3(J)+Q1(J)+Q2(J)+Q3(J)+R1(J)+R2(J)+R3(J)+
     1 P21(J)+P31(J)+P12(J)+Q21(J)+Q31(J)+Q12(J)+R21(J)+R31(J)+R12(J)
     2 +P32(J)+P13(J)+P23(J)+Q32(J)+Q13(J)+Q23(J)+R32(J)+R13(J)+R23(J)
   10  CONTINUE
C      unidade 6 mostra na tela o somatorio
       WRITE(6,102) (SUM(J),J=3,KTOT)
       J=3
   17   IF(J.GE.KTOT) GO TO 16
        X(J)=J*(J+1)

C       calculo dos fatores Franck-Condon, nao apresentando
C       dependencia rotacional de acordo com Singh 98

        FVVP(J)=fc(T)
        FVVR(J)=fc(T)
        FVVQ(J)=fc(T)

        P1(J)=P1(J)*FVVP(J)
        P2(J)=P2(J)*FVVP(J)
        P3(J)=P3(J)*FVVP(J)
        Q1(J)=Q1(J)*FVVQ(J)
        Q2(J)=Q2(J)*FVVQ(J)
        Q3(J)=Q3(J)*FVVQ(J)
        R1(J)=R1(J)*FVVR(J)
        R2(J)=R2(J)*FVVR(J)
        R3(J)=R3(J)*FVVR(J)
        J=J+1
        GO TO 17
   16  CONTINUE
       WRITE(9,100)
       DO 32 J=4,KTOT
       WRITE(9,101) J,P1(J),Q1(J),R1(J),P2(J),Q2(J),R2(J),
     * P3(J),Q3(J),R3(J)
   32  CONTINUE

       CLOSE(9)
       END DO

      STOP
  102  FORMAT('     SUM = ',10E11.3)
  100  FORMAT(6X,'J',8X,'P1N',8X,'Q1N',8X,'R1N',8X,'P2N',
     1 8X,'Q2N',8X,'R2N',8X,'P3N',8X,'Q3N',8X,'R3N')
  101  FORMAT(5X,I4,9(1X,E11.3))
  103  FORMAT(2X,3E15.5)
  104  FORMAT(I2,1X,I2,1X,A10,1x,E12.7)
       END
"""



















honllondon = honllondon_defaultdict(_new_honllondon)

