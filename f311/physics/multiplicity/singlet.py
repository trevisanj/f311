


def quanta_to_branch(Jl, J2l):
    """
    Singlet only has branches P/Q/R

    Args:
        Jl: J upper or J'
        J2l: J lower or  J''

    Returns: branch letter: "P"/"Q"/"R"
    """
    if Jl > J2l:
        return "R"
    elif Jl == J2l:
        return "Q"
    return "P"