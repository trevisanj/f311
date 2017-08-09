


def quanta_to_branch(Jl, J2l, spinl=None, spin2l=None):
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