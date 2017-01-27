"""OH Franck-Condom Factors as in B. Castilho's work (thesis)"""

__all__ = ["get_fcf_oh"]

__DICT = None


def get_fcf_oh(vl, v2l):
    """Returns Franck-Condon Factor for OH given (v', v'')"""
    global __DICT
    if __DICT is None:
        # First call, mounts dictionary
        __DICT = {}
        for vl_, v2l_, fcf in __FCF_OH:
            __DICT[(vl_, v2l_)] = fcf
    return __DICT[(vl, v2l)]


__FCF_OH = (
( 0,  0, .8638228E+00),
( 0,  1, .8712862E-01),
( 0,  2, .3144656E-01),
( 1,  0, .1320142E+00),
( 1,  1, .6831250E+00),
( 1,  2, .8655815E-01),
( 1,  3, .5471105E-01),
( 1,  4, .2221937E-01),
( 2,  1, .2115113E+00),
( 2,  2, .5983241E+00),
( 2,  3, .5548360E-01),
( 2,  4, .6503444E-01),
( 2,  5, .2923558E-01),
( 3,  2, .2344838E+00),
( 3,  3, .5794961E+00),
( 3,  4, .2249376E-01),
( 3,  5, .6799825E-01),
( 3,  6, .3022904E-01),
( 4,  3, .1998583E+00),
( 4,  4, .6001889E+00),
( 4,  5, .2535721E-02),
( 4,  6, .6969402E-01),
( 4,  7, .2711999E-01),
( 5,  3, .9234741E-01),
( 5,  4, .1242556E+00),
( 5,  5, .6290315E+00),
( 5,  6, .2994244E-02),
( 5,  7, .7392103E-01),
( 5,  8, .2248643E-01),
( 5,  9, .1669980E-01),
( 6,  4, .1363840E+00),
( 6,  5, .4541378E-01),
( 6,  6, .6366237E+00),
( 6,  7, .2473098E-01),
( 6,  8, .8013871E-01),
( 6,  9, .1874306E-01),
( 6, 10, .1382131E-01),
( 7,  5, .1538850E+00),
( 7,  6, .3036574E-02),
( 7,  7, .6094945E+00),
( 7,  8, .6004895E-01),
( 7,  9, .8373404E-01),
( 7, 10, .1770726E-01),
( 8,  6, .1324613E+00),
( 8,  8, .5636430E+00),
( 8, 10, .7621916E-01),
)