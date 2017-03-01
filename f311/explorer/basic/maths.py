"""
Low-level maths def's
"""


__all__ = ["bc_rubber", "rubberband", "_rubber_pieces", "poly_baseline"]


import numpy as np


def bc_rubber(vx):
    """
    Convex Polygonal Line baseline correction

    Args:
        vx: vector

    Returns: vx-rubberband(vx)
    """

    return vx-rubberband(vx)


def rubberband(vx):
    """
    Convex polygonal line (aka rubberband)

    Args:
        vx: 1-D numpy array

    Returns: the rubberband: a 1-D numpy array with same shape as vx

    This function stretches a polygonal line from below vx. The vertices of this multi-segment line
    will touch troughs of vx without crossing vx

    This was inspired on -- but is not equivalent to -- OPUS SB_Rubberband baseline correction [1].
    However, this one is parameterless, whereas OPUS RBBC asks for a number of points.

    References:
        [1] Bruker Optik GmbH, OPUS 5 Reference Manual. Ettlingen: Bruker, 2004.
    """
    pieces = [[vx[0]]]
    _rubber_pieces(vx, pieces)
    rubberband = np.concatenate(pieces)

    return rubberband


def _rubber_pieces(x, pieces):
    """Recursive function that add straight lines to list. Together, these lines form the rubberband."""
    nf = len(x)
    l = np.linspace(x[0], x[-1], nf)
    xflat = x - l
    idx = np.argmin(xflat)
    val = xflat[idx]
    if val < 0:
        _rubber_pieces(x[0:idx + 1], pieces)
        _rubber_pieces(x[idx:], pieces)
    else:
        pieces.append(l[1:])


def poly_baseline(flux, order, epsilon=None, maxit=None):
    """"
    Polynomial baseline

    Args:
      vx: np 1D array ("flux")
      order: polynomial order
      epsilon: tolerance to stop iterations. If zero or no value given, will default to sqrt(1/30*num_points)
      maxit: if informed, will restrict the maximum number of iterations to this value

    Returns: the baseline vector

    Reference: Beier BD, Berger AJ. Method for automated background subtraction from Raman spectra containing known
    contaminants. The Analyst. 2009; 134(6):1198-202. Available at: http://www.ncbi.nlm.nih.gov/pubmed/19475148.

    **Converted from MATLAB (IRootLab)**
    """

    nf = len(flux)
    if epsilon is None:
        # epsilon will be compared to a vector norm. If we assume the error at all elements to have the same importance, it
        # the norm of the error will be something like sqrt(nf*error_i)
        # For the tolerance to be 1 when nf = 1500 (empirically found to work) the formula below is set.
        epsilon = np.sqrt(1/90*nf);

    x = np.arange(1, nf+1) # x-values to be powered as columns of a design matrix
    M = np.zeros((nf, order+1))
    for i in range(0, order+1):
        M[:, i] = x**i
    MM = np.dot(M.T, M)
    flag_first = True
    it = 0
    while True:
        # (29/03/2011) Least-Squares solution is faster than polyfit()

        # Original formula in MATLAB: yp = (M*(MM\(M'*vx')))'
        yp = np.dot(M, (np.linalg.solve(MM, np.dot(M.T, flux)))).T

        flux = np.min(np.vstack((flux, yp)), 0)

        if not flag_first:
            if np.linalg.norm(flux-y_previous, 2) < epsilon:
                break
        else:
            flag_first = False

        y_previous = flux

        it += 1
        if it >= maxit:
            break

    return yp


