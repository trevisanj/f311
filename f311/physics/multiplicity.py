# coding: utf-8
"""
Multiplicity (Chemistry)

References:
    Istvan Kovacs, Rotational Structure in the spectra of diatomic molecules.
    American Elsevier, 1969

    https://en.wikipedia.org/wiki/Multiplicity_(chemistry)
"""


import math
from f311 import filetypes as ft
import a99

__all__ = ["multiplicity_toolbox", "NoLineStrength", "NO_LINE_STRENGTH"]


# Code to signal that there is no HLF for combination (vl, v2l, J, branch)
NO_LINE_STRENGTH = -999999

def _quanta_to_branch_singlet(Jl, J2l, spinl=None, spin2l=None):
    """
    Singlet only has branches P/Q/R

    Args:
        Jl: J upper or J'
        J2l: J lower or  J''
        spinl: ignored.
        spin2l: ignored

    Note: spinl, spin2l are present only to keep the interface consistent with
          .(singlet/doublet).quanta_to_branch()

    Returns: branch letter: "P"/"Q"/"R"
    """
    if Jl > J2l:
        return "R"
    elif Jl == J2l:
        return "Q"
    return "P"


def _quanta_to_branch_same_multiplicity(Jl, J2l, spinl=None, spin2l=None):
    """
    Converts quanta to branch for cases where the initial and final states have the same multiplicity, except singlets

    Args:
        Jl: J upper or J'
        J2l: J lower or  J''
        spinl:
        spin2l: (cannot be None)

    Returns:
        str: if spinl is None or equals spin2l, (letter)(number),
             otherwise (letter)(number)(number)

    >>> _quanta_to_branch_same_multiplicity(10.5, 11.5, spin2l=1)
    'P1'
    >>> _quanta_to_branch_same_multiplicity(11.5, 10.5, spin2l=2)
    'R2'
    >>> _quanta_to_branch_same_multiplicity(10.5, 10.5, spin2l=1)
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


class _MultiplicityToolbox(object):
    """
    Tools: Kovacz' "Line strength" and and quanta-to-branch conversion

    This class has descendants to handle specific cases. Basically, each descendant implements one
    table in Kovacs Chapter 3

    Usage:

        - Line strength: method get_sj()
        - convert quantum information to branch: method quanta_to_branch()
    """

    # # These values must be set at descendants
    # This allows for
    #     - automatically finding a suitable MultiplicityToolbox descendant given a system (e.g. A 2 Sigma - X 2 Pi)
    # and - error checking
    #
    # Possible values: "all", (Delta Lambda = LAML - LAM2L)
    #
    absDeltaLambda = None
    # 1 for singlet; 2 for doublet; 3 for triplet
    multiplicityl = None
    multiplicity2l = None
    # Method to convert quantum information to branch. **Use staticmethod()**!
    quanta_to_branch = None

    @property
    def dict_sj(self):
        return self._dict_sj

    def __init__(self, molconsts, flag_normalize=True):
        if not isinstance(molconsts, ft.MolConsts):
            raise TypeError("molconsts must be a MolConsts")
        self._molconsts = molconsts

        LAML = molconsts["from_spdf"]
        LAM2L = molconsts["to_spdf"]
        S = molconsts.get_S2l()

        if abs(LAML - LAM2L) != self.absDeltaLambda:
            raise ValueError("Invalid Delta Lambda {}. abs(Delta Lambda) must be {}". \
                             format(LAML-LAM2L, self.absDeltaLambda))

        if 2*S+1 != self.multiplicity2l:
            raise ValueError("**Sanity check fail**: Class {} expects multiplicity2l = 2*S+1 = {}, got {} instead". \
                             format(self.__class__.__name__, self.multiplicity2l, 2*S+1))

        self._dict_sj = {}

        #
        self._flag_normalize = flag_normalize

    def populate(self, vl, v2l, J):
        """Populates self.dict_sj with keys (vl, v2l, J, (all branches))"""
        data = self._get_populate_data(vl, v2l, J)
        self.__update_with_data(vl, v2l, J, data)

    def get_sj(self, vl, v2l, J, branch):
        """
        Returns Kovacz' "Line Strength", normalized or not

        Args:
            vl:
            v2l:
            J: **integer**
            branch: example: "P1"
        """

        J = int(J)

        key = (vl, v2l, J, branch)

        if key not in self._dict_sj:
            data = self._get_populate_data(vl, v2l, J)
            self.__update_with_data(vl, v2l, J, data)

        value = self._dict_sj[key]

        if value == NO_LINE_STRENGTH:
            raise NoLineStrength(
             "Cannot calculate line strength for (vl={}, v2l={}, J={}, branch='{}')".format(*key))

        return value

    def __update_with_data(self, vl, v2l, J, data):
        normalization_factor = 1.
        if self._flag_normalize:
            cc = self._molconsts
            normalization_factor = 2. / ((2 * cc.get_S2l() + 1) * (2 * J + 1) * (2 - cc.get_deltak()))

        for branch, function in data:
            try:
                value = function(J) * normalization_factor

                if isinstance(value, complex):
                    value = NO_LINE_STRENGTH

            except ZeroDivisionError:
                value = NO_LINE_STRENGTH
            self._dict_sj[(vl, v2l, J, branch)]  = value


    def _get_populate_data(self, vl, v2l, J):
        """Must be inherited and populate self with all branches for given (vl, v2l, J)"""
        raise NotImplementedError()

# Incomplete class (provided as example here, so far)
class _MTSinglet(_MultiplicityToolbox):
    absDeltaLambda = "all"
    multiplicityl = 1
    multiplicity2l = 1
    quanta_to_branch = staticmethod(_quanta_to_branch_singlet)


class _MTDoublet0(_MultiplicityToolbox):
    """
    Line strengths for (doublet, Delta Lambda = +-1)

    Formulas: Table 3.7 (p120); Formula 2.1.3-6 (p61)

    Adapted from Fortran code: ATMOS/wrk4/bruno/Mole/OH/sjoh.f
    """

    absDeltaLambda = 0
    multiplicityl = 2
    multiplicity2l = 2
    quanta_to_branch = staticmethod(_quanta_to_branch_same_multiplicity)

    def _get_populate_data(self, vl, v2l, J):
        cc = self._molconsts
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

        # TODO Ask BLB below
        # p61: “[...] Y= A/B. The term is called normal if A > 0, and inverted if A < 0”
        # p126: “in the case of inverted terms, Y is to be substituted with negative sign”
        if YL < 0:
            YL = -YL
        if Y2L < 0:
            Y2L = -Y2L

        # Kovacs formula 2.1.3-6
        UPLUSL = lambda J: ((LAML**2.)*YL*(YL-4) + 4*((J+0.5)**2.))**0.5 + LAML*(YL-2)
        UMINUSL= lambda J: ((LAML**2.)*YL*(YL-4) + 4*((J+0.5)**2.))**0.5 - LAML*(YL-2)
        CPLUSL = lambda J: 0.5*((UPLUSL(J)**2.) + 4*(((J+0.5)**2.) - LAML**2.))
        CMINUSL = lambda J: 0.5*((UMINUSL(J)**2.) + 4*(((J+0.5)**2.) - LAML**2.))
        UPLUS2L = lambda J: ((LAM2L**2.)*Y2L*(Y2L-4) + 4*((J+0.5)**2.))**0.5 + LAM2L*(Y2L-2)
        UMINUS2L = lambda J: ((LAM2L**2.)*Y2L*(Y2L-4) + 4*((J+0.5)**2.))**0.5 - LAM2L*(Y2L-2)
        CPLUS2L = lambda J: 0.5*((UPLUS2L(J)**2.) + 4*(((J+0.5)**2.)-LAM2L**2.))
        CMINUS2L = lambda J: 0.5*((UMINUS2L(J)**2.)+4*(((J+0.5)**2.)-LAM2L**2.))


        LAM = LAML  # remember, both LAML, LAM2L are the same


        # Some lost lambdas

        _P1 = lambda J: \
            (((J-LAM-0.5)*(J+LAM+0.5))/(4*J*CMINUSL(J-1)*CMINUS2L(J)))* \
            ((UMINUSL(J-1)*UMINUS2L(J) + 4*(J-LAM+0.5)*(J+LAM-0.5))**2.)

        _Q1 = lambda J: \
            ((J+0.5)/(2*J*(J+1)*CMINUSL(J)*CMINUS2L(J)))* \
            (((LAM+0.5)*UMINUSL(J)*UMINUS2L(J) + 4*(LAM-0.5)*(J-LAM+0.5)*(J+LAM+0.5))**2.)

        _R1 = lambda J: \
            (((J-LAM+0.5)*(J+LAM+1.5))/(4*(J+1)*CMINUSL(J+1)*CMINUS2L(J)))* \
            ((UMINUSL(J+1)*UMINUS2L(J) + 4*(J-LAM+1.5)*(J+LAM+0.5))**2.)

        _P21 = lambda J: \
            (((J-LAM-0.5)*(J+LAM+0.5))/(4*J*CPLUSL(J-1)*CMINUS2L(J)))* \
            ((UPLUSL(J-1)*UMINUS2L(J) - 4*(J-LAM+0.5)*(J+LAM-0.5))**2)

        _Q21 = lambda J: \
            (((J+0.5))/(2*J*(J+1)*CPLUSL(J)*CMINUS2L(J)))* \
            ((LAM+0.5)*(UPLUSL(J)*UMINUS2L(J) - 4*(LAM-0.5)*(J-LAM+0.5)*(J+LAM+0.5))**2.)

        _R21 = lambda J: \
            (((J-LAM+0.5)*(J+LAM+1.5))/(4*(J+1)*CPLUSL(J+1)*CMINUS2L(J)))* \
            ((UPLUSL(J+1)*UMINUS2L(J) - 4*(J-LAM+1.5)*(J+LAM+0.5))**2.)

        _P12 = lambda J: \
            (((J-LAM-0.5)*(J+LAM+0.5))/(4*J*CMINUSL(J-1)*CPLUS2L(J)))* \
            ((UMINUSL(J-1)*UPLUS2L(J) - 4*(J-LAM+0.5)*(J+LAM-0.5))**2.)

        _Q12 = lambda J: \
            (((J+0.5))/(2*J*(J+1)*CMINUSL(J)*CPLUS2L(J)))*\
            ((LAM+0.5)*(UMINUSL(J)*UPLUS2L(J) - 4*(LAM-0.5)*(J-LAM+0.5)*(J+LAM+0.5))**2.)

        _R12 = lambda J: \
            (((J-LAM+0.5)*(J+LAM+1.5))/(4*(J+1)*CMINUSL(J+1)*CPLUS2L(J)))* \
            ((UMINUSL(J+1)*UPLUS2L(J) - 4*(J-LAM+1.5)*(J+LAM+0.5))**2.)

        _P2 = lambda J: \
            (((J-LAM-0.5)*(J+LAM+0.5))/(4*J*CPLUSL(J-1)*CPLUS2L(J)))* \
            ((UPLUSL(J-1)*UPLUS2L(J) + 4*(J-LAM+0.5)*(J+LAM-0.5))**2.)

        _Q2 = lambda J: \
            (((J+0.5))/(2*J*(J+1)* CPLUSL(J)*CPLUS2L(J)))* \
            ((LAM+0.5)*(UPLUSL(J)*UPLUS2L(J) + 4*(LAM-0.5)*(J-LAM+0.5)*(J+LAM+0.5))**2.)

        _R2 = lambda J: \
            (((J-LAM+0.5)*(J+LAM+1.5))/(4*(J+1)*CPLUSL(J+1)*CPLUS2L(J)))* \
            ((UPLUSL(J+1)*UPLUS2L(J) + 4*(J-LAM+1.5)*(J+LAM+0.5))**2.)

        return (
         ("P1", _P1),
         ("Q1", _Q1),
         ("R1", _R1),
         ("P21", _P21),
         ("Q21", _Q21),
         ("R21", _R21),
         ("P12", _P12),
         ("Q12", _Q12),
         ("R12", _R12),
         ("P2", _P2),
         ("Q2", _Q2),
         ("R2", _R2),
        )


class _MTDoublet1(_MultiplicityToolbox):
    """
    Line strengths for (doublet, Delta Lambda = +-1)

    Formulas: Table 3.7 (p120); Formula 2.1.3-6 (p61)

    Adapted from Fortran code: ATMOS/wrk4/bruno/Mole/OH/sjoh.f
    """

    absDeltaLambda = 1
    multiplicityl = 2
    multiplicity2l = 2
    quanta_to_branch = staticmethod(_quanta_to_branch_same_multiplicity)

    def _get_populate_data(self, vl, v2l, J):
        cc = self._molconsts
        LAML = cc["from_spdf"]
        LAM2L = cc["to_spdf"]
        AL = cc["statel_A"]
        AEL = cc["statel_alpha_e"]
        BEL = cc["statel_B_e"]
        A2L = cc["state2l_A"]
        AE2L = cc["state2l_alpha_e"]
        BE2L = cc["state2l_B_e"]

        # Original comment:
        #
        #     cada banda possue valores distintos de Y' e Y''
        #     quando Y=A/B > 0, temos o termo normal, por isso
        #     nao se modifica as formulas abaixo



        BL = BEL - AEL * (vl + 0.5)
        B2L = BE2L - AE2L * (v2l + 0.5)

        YL = AL / BL
        Y2L = A2L / B2L


        # p61: “[...] Y= A/B. The term is called normal if A > 0, and inverted if A < 0”
        # p126: “in the case of inverted terms, Y is to be substituted with negative sign”
        if YL < 0:
            YL = -YL
        if Y2L < 0:
            Y2L = -Y2L


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


        # Resolves the Delta Lambda = LAML - LAM2L

        if LAML > LAM2L:
            return (
             ("P1", _P1),
             ("Q1", _Q1),
             ("R1", _R1),
             ("P21", _P21),
             ("Q21", _Q21),
             ("R21", _R21),
             ("P12", _P12),
             ("Q12", _Q12),
             ("R12", _R12),
             ("P2", _P2),
             ("Q2", _Q2),
             ("R2", _R2),
            )

        elif LAML < LAM2L:
            return (
             ("P1", lambda J: _R1(J-1)),
             ("Q1", _Q1),
             ("R1", lambda J: _P1(J+1)),
             ("P21", lambda J: _R12(J-1)),
             ("Q21", _Q12),
             ("R21", lambda J: _P12(J+1)),
             ("P12", lambda J: _R21(J-1)),
             ("Q12", _Q21),
             ("R12", lambda J: _P21(J+1)),
             ("P2", lambda J: _R2(J-1)),
             ("Q2", _Q2),
             ("R2", lambda J: _P2(J+1)),
            )


class _MTTriplet1(_MultiplicityToolbox):
    """
    Honl-London factors for (triplet, Delta Lambda = +-1)

    Formulas: Table 3.10 (p136-p137); Formulas 2.1.4-8 to 2.1.4-10 (p69-p70)

    Adapted from Fortran code: ATMOS/wrk4/bruno/Mole/NH/sjnh.f
    """

    absDeltaLambda = 1
    multiplicityl = 3
    multiplicity2l = 3
    quanta_to_branch = staticmethod(_quanta_to_branch_same_multiplicity)

    def _get_populate_data(self, vl, v2l, J):
        cc = self._molconsts
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


        _P1 = lambda J: \
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
            return (
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

        elif LAML < LAM2L:
            return (
             ("P1", lambda J: _R1(J-1)),
             ("Q1", _Q1),
             ("R1", lambda J: _P1(J+1)),
             ("P21", _R12(J-1)),
             ("Q21", _Q12),
             ("R21", lambda J: _P12(J+1)),
             ("P31", lambda J: _R13(J-1)),
             ("Q31", _Q13),
             ("R31", lambda J: _P13(J+1)),
             ("P12", lambda J: _R21(J-1)),
             ("Q12", _Q21),
             ("R12", lambda J: _P21(J+1)),
             ("P2", lambda J: _R2(J-1)),
             ("Q2", _Q2),
             ("R2", lambda J: _P2(J+1)),
             ("P32", lambda J: _R23(J-1)),
             ("Q32", _Q23),
             ("R32", lambda J: _P23(J+1)),
             ("P13", lambda J: _R31(J-1)),
             ("Q13", _Q31),
             ("R13", lambda J: _P31(J+1)),
             ("P23", lambda J: _R32(J-1)),
             ("Q23", _Q32),
             ("R23", lambda J: _P32(J+1)),
             ("P3", lambda J: _R3(J-1)),
             ("Q3", _Q3),
             ("R3", lambda J: _P3(J+1)),
            )


# TODO multiplicity is not the best term, should be sth more towards "transition"
def multiplicity_toolbox(molconsts, flag_normalize=None):
    """Factory function that returns a MultiplicityToolbox descendant appropriate to molconsts"""

    C = [_MTSinglet, _MTDoublet0, _MTDoublet1, _MTTriplet1]

    absDeltaLambda = abs(molconsts["from_spdf"]-molconsts["to_spdf"])

    for cls in C:
        if (cls.absDeltaLambda == "all" or cls.absDeltaLambda == absDeltaLambda) and \
           cls.multiplicityl == molconsts["from_mult"] and \
           cls.multiplicity2l == molconsts["to_mult"]:
            return cls(molconsts, flag_normalize)

    raise ValueError("Could not find a suitable class for given molecular constants "
     "(I need abs(\u0394\u039B)={}; multiplicity'={}; multiplicity''={})".format(
     int(absDeltaLambda), int(molconsts["from_mult"]), int(molconsts["to_mult"])))


class NoLineStrength(Exception):
    pass