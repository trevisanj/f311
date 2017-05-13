"""
Hönl-London factors for doublets, formulas from Kovacs 1969 p130
"""

from collections import OrderedDict

__all__ = ["get_honllondon_formulas", "quanta_to_branch"]


def quanta_to_branch(Jl, J2l, spinl=None, spin2l=None):
    """
    Singlet only has branches P/Q/R

    Args:
        Jl: J upper or J'
        J2l: J lower or  J''
        spinl:
        spin2l: (cannot be None)

    Returns: branch letter: "P"/"Q"/"R"

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
        assert spin2l is not None, "spin2l cannot be None"
        if spinl == spin2l:
            ret = "{}{:1d}".format(br, spin2l)
        else:
            ret = "{}{:1d}{:1d}".format(br, spinl, spin2l)
    return ret


def get_honllondon_formulas(LAML, LAM2L):
    """Function factory: returns (P1(J), Q1(J), ...)

    Args:
        LAML: Lambda sup:
          0 for Sigma
          1 for Pi
          2 for Delta
          3 for Phi
        LAM2L: Lambda inf (0/1/2/3 as above)

    Returns:
        dictionary with keys (P1, Q1, R1, P21, Q21, R21, P12, Q12, R12, P2, Q2, R2)

    all functions are functions of J, i.e., P1 = P1(J) (they are adjusted for specific LAML, LAM2L)

    Order as in Kovacs 1969, p130, 1st column

    Examples:

    >>> formulas = get_honllondon_formulas(1, 0)

    >>> formulas = get_honllondon_formulas(0, 1)

    >>> J = 10.5
    >>> formulas = get_honllondon_formulas(1, 0)  # delta Lambda = +1
    >>> p1, q1, r1, p21, q21, r21, p12, q12, r12, p2, q2, r2 = [f(J) for f in formulas.values()]

    >>> J = 10.5
    >>> formulas = get_honllondon_formulas(1, 0)  # delta Lambda = +1
    >>> [f(J) for f in formulas.values()]
    [4.714285714285714, 10.952380952380953, 6.260869565217392, 0.047619047619047616, 0.02484472049689441, 0.0, 0.0, 0.020703933747412008, 0.043478260869565216, 4.761904761904762, 10.956521739130435, 6.217391304347826]


    **Sanity check examples**. In the following examples, the sum of all "normalized" Hönl-London
    factors (HLF) for a given J must be 1 ("higher-order" branches are not considered because their
    HLFs are negligible.

    >>> S, DELTAK = 0.5, 0  # spin, delta Kronecker
    >>> J = 3
    >>> factor = 2/((2*J+1)*(2*S+1)*(2-DELTAK))
    >>> normalized = [f(J)*factor for f in get_honllondon_formulas(0, 1).values()]
    >>> normalized
    [0.14583333333333334, 0.23809523809523808, 0.10044642857142856, 0.011904761904761906, 0.003720238095238095, 0.0, 0.0, 0.006696428571428571, 0.008928571428571428, 0.13392857142857142, 0.24107142857142855, 0.109375]
    >>> sum(normalized)
    0.9999999999999998


    >>> S, DELTAK = 0.5, 0  # spin, delta Kronecker
    >>> J = 1.5
    >>> factor = 2/((2*J+1)*(2*S+1)*(2-DELTAK))
    >>> normalized = [f(J)*factor for f in get_honllondon_formulas(0, 1).values()]
    >>> sum(normalized)
    1.0
    """

    if LAML > LAM2L:
        ret = OrderedDict((("P1", lambda J: formula0(J, LAML, LAM2L)),
                           ("Q1", lambda J: formula1(J, LAML, LAM2L)),
                           ("R1", lambda J: formula2(J, LAML, LAM2L)),
                           ("P21", lambda J: formula3(J, LAML, LAM2L)),
                           ("Q21", lambda J: formula4(J, LAML, LAM2L)),
                           ("R21", lambda J: formula5(J, LAML, LAM2L)),
                           ("P12", lambda J: formula6(J, LAML, LAM2L)),
                           ("Q12", lambda J: formula7(J, LAML, LAM2L)),
                           ("R12", lambda J: formula8(J, LAML, LAM2L)),
                           ("P2", lambda J: formula9(J, LAML, LAM2L)),
                           ("Q2", lambda J: formula10(J, LAML, LAM2L)),
                           ("R2", lambda J: formula11(J, LAML, LAM2L)),
                         ))
    elif LAML < LAM2L:
        ret = OrderedDict((("P1", lambda J: formula2(J-1, LAM2L, LAML)),
                           ("Q1", lambda J: formula1(J, LAM2L, LAML)),
                           ("R1", lambda J: formula0(J+1, LAM2L, LAML)),
                           ("P21", lambda J: formula8(J-1, LAM2L, LAML)),
                           ("Q21", lambda J: formula7(J, LAM2L, LAML)),
                           ("R21", lambda J: formula6(J+1, LAM2L, LAML)),
                           ("P12", lambda J: formula5(J-1, LAM2L, LAML)),
                           ("Q12", lambda J: formula4(J, LAM2L, LAML)),
                           ("R12", lambda J: formula3(J+1, LAM2L, LAML)),
                           ("P2", lambda J: formula11(J-1, LAM2L, LAML)),
                           ("Q2", lambda J: formula10(J, LAM2L, LAML)),
                           ("R2", lambda J: formula9(J+1, LAM2L, LAML)),
                         ))
    else:
        raise ValueError("Invalid delta Lambda")

    return ret


def UPLUSL(J, LBIG):
    return 2. * (J - LBIG + 0.5)


def UMINUSL(J, LBIG):
    return 2. * (J + LBIG + 0.5)


def CPLUSL(J, LBIG):
    return 4. * (J + 0.5) * (J - LBIG + 0.5)


def CMINUSL(J, LBIG):
    return 4. * (J + 0.5) * (J + LBIG + 0.5)


def UPLUS2L(J, LSMALL):
    return 2.*(J-LSMALL+0.5)


def UMINUS2L(J, LSMALL):
    return 2.*(J+LSMALL+0.5)


def CPLUS2L(J, LSMALL):
    return 4.*(J+0.5)*(J-LSMALL+0.5)


def CMINUS2L(J, LSMALL):
    return 4.*(J+0.5)*(J+LSMALL+0.5)


def formula0(J, LBIG, LSMALL):
    """Formula for P1(J) or R1(J-1)"""
    return (((J-LSMALL-1.5)*(J-LSMALL-0.5))/(8*J*CMINUSL(J-1, LBIG)*
    CMINUS2L(J, LSMALL)))*((UMINUSL(J-1, LBIG)*UMINUS2L(J, LSMALL) +
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)

def formula1(J, LBIG, LSMALL):
    """Formula for Q1(J)"""
    return (((J-LSMALL-0.5)*(J+0.5)*(J+LSMALL+1.5))/(4*J*(J+1)*
    CMINUSL(J, LBIG)*CMINUS2L(J, LSMALL)))*((UMINUSL(J, LBIG)*UMINUS2L(J, LSMALL) +
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula2(J, LBIG, LSMALL):
    """Formula for R1(J) or P1(J+1)"""
    return (((J+LSMALL+1.5)*(J+LSMALL+2.5))/(8*(J+1)*CMINUSL(J+1, LBIG)*
    CMINUS2L(J, LSMALL)))*((UMINUSL(J+1, LBIG)*UMINUS2L(J, LSMALL) +
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)

     #   P1(J+1)=(((J+LAM2L+1.5)*(J+LAM2L+2.5))/(8*(J+1)*CMENOSL(J+1)*
     # 1 CMENOS2L(J)))*((UMENOSL(J+1)*UMENOS2L(J) +
     # 2 4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)


def formula3(J, LBIG, LSMALL):
    """Formula for P21(J) or R12(J-1)"""
    return (((J-LSMALL-1.5)*(J-LSMALL-0.5))/(8*J*CPLUSL(J-1, LBIG)*
    CMINUS2L(J, LSMALL)))*((UPLUSL(J-1, LBIG)*UMINUS2L(J, LSMALL) -
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula4(J, LBIG, LSMALL):
    """Formula for Q21(J) or Q12(J)"""
    return (((J-LSMALL-0.5)*(J+0.5)*(J+LSMALL+1.5))/(4*J*(J+1)*
    CPLUSL(J, LBIG)*CMINUS2L(J, LSMALL)))*((UPLUSL(J, LBIG)*UMINUS2L(J, LSMALL) -
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)

def formula5(J, LBIG, LSMALL):
    """Formula for R21(J) or P12(J+1)"""
    return (((J+LSMALL+1.5)*(J+LSMALL+2.5))/(8*(J+1)*CPLUSL(J+1, LBIG)*
    CMINUS2L(J, LSMALL)))*((UPLUSL(J+1, LBIG)*UMINUS2L(J, LSMALL) -
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula6(J, LBIG, LSMALL):
    """Formula for P21(J) or R21(J-1)"""
    return (((J-LSMALL-1.5)*(J-LSMALL-0.5))/
           (8*J*CMINUSL(J-1, LBIG)*CPLUS2L(J, LSMALL)))*\
           ((UMINUSL(J-1, LBIG)*UPLUS2L(J, LSMALL) - 4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula7(J, LBIG, LSMALL):
    """Formula for Q12(J) or Q21(J)"""
    return (((J-LSMALL-0.5)*(J+0.5)*(J+LSMALL+1.5))/(4*J*(J+1)*
    CMINUSL(J, LBIG)*CPLUS2L(J, LSMALL)))*((UMINUSL(J, LBIG)*UPLUS2L(J, LSMALL) -
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula8(J, LBIG, LSMALL):
    """Formula for R12(J) or P21(J+1)"""
    return (((J+LSMALL+1.5)*(J+LSMALL+2.5))/(8*(J+1)*CMINUSL(J+1, LBIG)*
    CPLUS2L(J, LSMALL)))*((UMINUSL(J+1, LBIG)*UPLUS2L(J, LSMALL) -
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula9(J, LBIG, LSMALL):
    """Formula for P2(J) or R2(J-1)"""
    return (((J-LSMALL-1.5)*(J-LSMALL-0.5))/(8*J*CPLUSL(J-1, LBIG)*
    CPLUS2L(J, LSMALL)))*((UPLUSL(J-1, LBIG)*UPLUS2L(J, LSMALL) +
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula10(J, LBIG, LSMALL):
    """Formula for Q2(J)"""
    return (((J-LSMALL-0.5)*(J+0.5)*(J+LSMALL+1.5))/(4*J*(J+1)*
    CPLUSL(J, LBIG)*CPLUS2L(J, LSMALL)))*((UPLUSL(J, LBIG)*UPLUS2L(J, LSMALL) +
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


def formula11(J, LBIG, LSMALL):
    """Formula for R2(J) or P2(J+1)"""
    return (((J+LSMALL+1.5)*(J+LSMALL+2.5))/(8*(J+1)*CPLUSL(J+1, LBIG)*
    CPLUS2L(J, LSMALL)))*((UPLUSL(J+1, LBIG)*UPLUS2L(J, LSMALL) +
    4*(J-LSMALL+0.5)*(J+LSMALL+0.5))**2.)


# """
# Hönl-London factors for doublets, formulas from Kovacs 1969 p130
#
# References:
#     [1] Istvan Kovacs, Rotational Structure in the spectra of diatomic molecules.
#         American Elsevier, 1969
#
# """
#
# from collections import OrderedDict
#
# __all__ = ["get_honllondon_formulas", "quanta_to_branch"]
#
#
#
#
# def quanta_to_branch(Jl, J2l, spin):
#     """
#     Singlet only has branches P/Q/R
#
#     Args:
#         Jl: J upper or J'
#         J2l: J lower or  J''
#
#     Returns: branch letter: "P"/"Q"/"R"
#
#     Example:
#
#     >>> quanta_to_branch(10.5, 11.5, 1)
#     'P1'
#     >>> quanta_to_branch(11.5, 10.5, 2)
#     'R2'
#     >>> quanta_to_branch(10.5, 10.5, 1)
#     'Q1'
#
#     """
#     if Jl > J2l:
#         br = "R"
#     elif Jl == J2l:
#         br =  "Q"
#     else:
#         br = "P"
#     ret = "{}{:1d}".format(br, spin)
#     return ret
#
#
# def get_honllondon_formulas(LAML, LAM2L):
#     """Function factory: returns (P1(J), Q1(J), ...)
#
#     Args:
#         LAML: Lambda sup:
#           0 for Sigma
#           1 for Pi
#           2 for Delta
#           3 for Phi
#         LAM2L: Lambda inf (0/1/2/3 as above)
#
#     Returns:
#         dictionary with keys (P1, Q1, R1, P21, Q21, R21, P12, Q12, R12, P2, Q2, R2)
#
#     all functions are functions of J, i.e., P1 = P1(J) (they are adjusted for specific LAML, LAM2L)
#
#     Order as in Kovacs 1969, p130, 1st column
#
#     Examples:
#
#     >>> formulas = get_honllondon_formulas(1, 0)
#
#     >>> formulas = get_honllondon_formulas(0, 1)
#
#     >>> J = 10.5
#     >>> formulas = get_honllondon_formulas(1, 0)  # delta Lambda = +1
#     >>> p1, q1, r1, p21, q21, r21, p12, q12, r12, p2, q2, r2 = [f(J) for f in formulas.values()]
#
#     >>> J = 10.5
#     >>> formulas = get_honllondon_formulas(1, 0)  # delta Lambda = +1
#     >>> [f(J) for f in formulas.values()]
#     [4.714285714285714, 10.952380952380953, 6.260869565217392, 0.047619047619047616, 0.02484472049689441, 0.0, 0.0, 0.020703933747412008, 0.043478260869565216, 4.761904761904762, 10.956521739130435, 6.217391304347826]
#
#     >>> S, DELTAK = 0.5, 0  # spin, delta Kronecker
#     >>> J = 3
#     >>> factor = 2/((2*J+1)*(2*S+1)*(2-DELTAK))
#     >>> normalized = [f(J)*factor for f in get_honllondon_formulas(0, 1).values()]
#     >>> normalized
#     [0.10714285714285715, 0.24891774891774893, 0.1422924901185771, 0.0010822510822510823, 0.0005646527385657821, 0.0, 0.0, 0.0004705439488048184, 0.0009881422924901185, 0.10822510822510822, 0.24901185770750991, 0.14130434782608697]
#     >>> sum(normalized)
#     1.0
#
#     >>> S, DELTAK = 0.5, 0  # spin, delta Kronecker
#     >>> J = 1.5
#     >>> factor = 2/((2*J+1)*(2*S+1)*(2-DELTAK))
#     >>> normalized = [f(J)*factor for f in get_honllondon_formulas(0, 1).values()]
#     >>> sum(normalized)
#     1.0
#     """
#
#     if LAML > LAM2L:
#         ret = OrderedDict((("P1", lambda J: formula0(J, LAML, LAM2L)),
#                            ("Q1", lambda J: formula1(J, LAML, LAM2L)),
#                            ("R1", lambda J: formula2(J, LAML, LAM2L)),
#                            ("P21", lambda J: formula3(J, LAML, LAM2L)),
#                            ("Q21", lambda J: formula4(J, LAML, LAM2L)),
#                            ("R21", lambda J: formula5(J, LAML, LAM2L)),
#                            ("P12", lambda J: formula6(J, LAML, LAM2L)),
#                            ("Q12", lambda J: formula7(J, LAML, LAM2L)),
#                            ("R12", lambda J: formula8(J, LAML, LAM2L)),
#                            ("P2", lambda J: formula9(J, LAML, LAM2L)),
#                            ("Q2", lambda J: formula10(J, LAML, LAM2L)),
#                            ("R2", lambda J: formula11(J, LAML, LAM2L)),
#                          ))
#     elif LAML < LAM2L:
#         ret = OrderedDict((("P1", lambda J: formula2(J-1, LAML, LAM2L)),
#                            ("Q1", lambda J: formula1(J, LAML, LAM2L)),
#                            ("R1", lambda J: formula0(J+1, LAML, LAM2L)),
#                            ("P21", lambda J: formula8(J-1, LAML, LAM2L)),
#                            ("Q21", lambda J: formula7(J, LAML, LAM2L)),
#                            ("R21", lambda J: formula6(J+1, LAML, LAM2L)),
#                            ("P12", lambda J: formula5(J-1, LAML, LAM2L)),
#                            ("Q12", lambda J: formula4(J, LAML, LAM2L)),
#                            ("R12", lambda J: formula3(J+1, LAML, LAM2L)),
#                            ("P2", lambda J: formula11(J-1, LAML, LAM2L)),
#                            ("Q2", lambda J: formula10(J, LAML, LAM2L)),
#                            ("R2", lambda J: formula9(J+1, LAML, LAM2L)),
#                          ))
#     else:
#         raise ValueError("Invalid delta Lambda")
#
#     return ret
#
#
# def UPLUS(J, LAM):
#     """Formula (3), p. 128"""
#     return 2. * (J - LAM + 0.5)
#
# def UMINUS(J, LAM):
#     """Formula (3), p. 128"""
#     return 2. * (J + LAM + 0.5)
#
# def CPLUS(J, LAM):
#     """Formula (3), p. 128"""
#     return 4. * (J + 0.5) * (J - LAM + 0.5)
#
# def CMINUS(J, LAM):
#     """Formula (3), p. 128"""
#     return 4. * (J + 0.5) * (J + LAM + 0.5)
#
#
# def formula0(J, LAML, LAM2L):
#     """Table 3.7 (p. 130): Formula for P1(J) or R1(J-1)"""
#     return (((J-LAM2L-1.5)*(J-LAM2L-0.5))/(8*J*CMINUS(J-1, LAML)*
#     CMINUS(J, LAM2L)))*((UMINUS(J-1, LAML)*UMINUS(J, LAM2L) +
#     4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)
#
# def formula1(J, LAML, LAM2L):
#     """Table 3.7 (p. 130): Formula for Q1(J)"""
#     return (((J-LAM2L-0.5)*(J+0.5)*(J+LAM2L+1.5))/(4*J*(J+1)*
#     CMINUS(J, LAML)*CMINUS(J, LAM2L)))*((UMINUS(J, LAML)*UMINUS(J, LAM2L) +
#     4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)
#
#
# def formula2(J, LAML, LAM2L):
#     """Table 3.7 (p. 130): Formula for R1(J) or P1(J+1)"""
#     return (((J+LAM2L+1.5)*(J+LAM2L+2.5))/(8*(J+1)*CMINUS(J+1, LAML)*
#     CMINUS(J, LAM2L)))*((UMINUS(J+1, LAML)*UMINUS(J, LAM2L) +
#     4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)
#
#      #   P1(J+1)=(((J+LAM2L+1.5)*(J+LAM2L+2.5))/(8*(J+1)*CMENOSL(J+1)*
#      # 1 CMENOS2L(J)))*((UMENOSL(J+1)*UMENOS2L(J) +
#      # 2 4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)
#
#
# def formula3(J, LAML, LAM2L):
#     """Table 3.7 (p. 130): Formula for P21(J) or R12(J-1)"""
#     return (((J-LAM2L-1.5)*(J-LAM2L-0.5))/(8*J*CPLUS(J-1, LAML)*
#     CMINUS(J, LAM2L)))*((UPLUS(J-1, LAML)*UMINUS(J, LAM2L) -
#     4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)
#
#
# def formula4(J, LAML, LAM2L):
#     """Table 3.7 (p. 130): Formula for Q21(J) or Q12(J)"""
#     return (((J-LAM2L-0.5)*(J+0.5)*(J+LAM2L+1.5))/(4*J*(J+1)*
#     CPLUS(J, LAML)*CMINUS(J, LAM2L)))*((UPLUS(J, LAML)*UMINUS(J, LAM2L) -
#     4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)
#
# def formula5(J, LAML, LAM2L):
#     """Table 3.7 (p. 130): Formula for R21(J) or P12(J+1)"""
#     return (((J+LAM2L+1.5)*(J+LAM2L+2.5))/(8*(J+1)*CPLUS(J+1, LAML)*
#     CMINUS(J, LAM2L)))*((UPLUS(J+1, LAML)*UMINUS(J, LAM2L) -
#     4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)
#
#
# def formula6(J, LAML, LAM2L):
#     """Table 3.7 (p. 130): Formula for P21(J) or R21(J-1)"""
#     return (((J-LAM2L-1.5)*(J-LAM2L-0.5))/(8*J*CMINUS(J-1, LAML)*
#     CPLUS(J, LAM2L)))*((UMINUS(J-1, LAML)*UPLUS(J, LAM2L) -
#     4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)
#
#
# def formula7(J, LAML, LAM2L):
#     """Table 3.7 (p. 130): Formula for Q12(J) or Q21(J)"""
#     return (((J-LAM2L-0.5)*(J+0.5)*(J+LAM2L+1.5))/(4*J*(J+1)*
#     CMINUS(J, LAML)*CPLUS(J, LAM2L)))*((UMINUS(J, LAML)*UPLUS(J, LAM2L) -
#     4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)
#
#
# def formula8(J, LAML, LAM2L):
#     """Table 3.7 (p. 130): Formula for R12(J) or P21(J+1)"""
#     return (((J+LAM2L+1.5)*(J+LAM2L+2.5))/(8*(J+1)*CMINUS(J+1, LAML)*
#     CPLUS(J, LAM2L)))*((UMINUS(J+1, LAML)*UPLUS(J, LAM2L) -
#     4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)
#
#
# def formula9(J, LAML, LAM2L):
#     """Table 3.7 (p. 130): Formula for P2(J) or R2(J-1)"""
#     return (((J-LAM2L-1.5)*(J-LAM2L-0.5))/(8*J*CPLUS(J-1, LAML)*
#     CPLUS(J, LAM2L)))*((UPLUS(J-1, LAML)*UPLUS(J, LAM2L) +
#     4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)
#
#
# def formula10(J, LAML, LAM2L):
#     """Table 3.7 (p. 130): Formula for Q2(J)"""
#     return (((J-LAM2L-0.5)*(J+0.5)*(J+LAM2L+1.5))/(4*J*(J+1)*
#     CPLUS(J, LAML)*CPLUS(J, LAM2L)))*((UPLUS(J, LAML)*UPLUS(J, LAM2L) +
#     4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)
#
#
# def formula11(J, LAML, LAM2L):
#     """Table 3.7 (p. 130): Formula for R2(J) or P2(J+1)"""
#     return (((J+LAM2L+1.5)*(J+LAM2L+2.5))/(8*(J+1)*CPLUS(J+1, LAML)*
#     CPLUS(J, LAM2L)))*((UPLUS(J+1, LAML)*UPLUS(J, LAM2L) +
#     4*(J-LAM2L+0.5)*(J+LAM2L+0.5))**2.)

