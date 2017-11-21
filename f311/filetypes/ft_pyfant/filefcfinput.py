from .. import DataFile
import a99
from ..molconsts import *
from ..basic import state_to_str, SS_PLAIN


__all__ = ["FileFCFInput", "FCFInputState"]


class FCFInputState(object):
    """Describes one of the two states in FileFCFInput"""

    def __init__(self, title="", ni=0, ns=1, igraph=0, ienerg=0, istate=2, zmu=0., rmin=0.75, rmax=3.5,
                 delr=0.005, maxv=12, be=0., de=0., kdmaxv=12, neig=0, ev=None, bv=None):

        if ev is None:
            ev = []
        if bv is None:
            bv = []

        self.title = title

        # First 5 values we always leave as (0, 1, 0, 0, 2) [AAA]
        # = 0 ALLOWS DENSITY GRAPHS TO BE PRODUCED.OTHER VALUES DO NO
        self.ni = ni
        # GIVES ORTHOGONALITY TEST IF = 1
        self.ns = ns
        self.igraph = igraph
        self.ienerg = ienerg
        # = 2 FOR A TRANSITION = 1 FOR A SINGLE STATE
        self.istate = istate
        # "reduced mass" (m1*m2)/(m1+m2) (m*: atomic masses in the diatomic molecule) [AAA]
        self.zmu = zmu
        # MINIMUM RADIUS FOR CALCULATION OF WAVEFUNCTIONS
        self.rmin = rmin
        # MAXIMUM RADIUS FOR CALCULATION OF WAVEFUNCTIONS
        self.rmax = rmax
        # RADIAL INTERVAL FOR CALCULATION OF WAVEFUNCTIONS
        self.delr = delr
        # MAXIMUM QUANTUM NUMBER [i.e., vibrational, "v"] FOR CALCULATION OF RESULTS
        self.maxv = maxv
        # EQUILBRIUM ROTATIONAL CONSTANT [B_e from NIST or other source]
        self.be = be
        # DISSOCIATION ENERGY OR ESTIMATE THEREOF
        self.de = de
        # MAXIMUM QUANTUM NUMBER FOR CALCULATION OF KLEIN DUNHAM
        # POTENTIAL.MUST BE AT LEAST 2 AND NOT MORE THAN 30
        self.kdmaxv = kdmaxv
        # USED FOR WORK IN THE CONTINUUM, NUMBER OF ENERGY LEVELS
        # TO CALCULATE CONTINUUM WAVEFUNCTIONS AT
        self.neig = neig
        self.ev = ev
        self.bv = bv

    def __repr__(self):
        attrs = ["title", "ni", "ns", "igraph", "ienerg", "istate", "zmu", "rmin", "rmax", "delr", "maxv",
                 "be", "de", "kdmaxv", "neig", "ev", "bv"]
        return a99.make_code_readable("{}({})".format(self.__class__.__name__, ", ".join(["{}={}".format(x, repr(getattr(self, x))) for x in attrs])))


class FileFCFInput(DataFile):
    """
    Input file for Franck-Condon factors (FCF) calculation program

    **History**: See FileFCF

    Here is one annotated sample file:

    ```
                                                               ISTATE
                                                            IENERG  |
                                                         IGRAPH  |  |
                                                       NI NS  |  |  |
    TITLE---------------------------------------------  |  |  |  |  |
    1  OH A DOUBLET SIGMA UPPER STATE                   0  1  0  0  2

    ZMU-------RMIN------RMAX------DELR------
    0.9480871     0.750     3.500     0.005


    MAXV
    ---       BE        DE                                        KDMAXV NEIG
      |       ----------==========                                    ===---
     12           17.358  35000.00                                     12

    EV(32)
         00.00   1565.99   4554.82   7351.07   9959.53  12392.75  14671.06  16822.54
      18883.03  20896.17  22913.33  24993.67  27204.10  29619.32

    BV(32)
       17.3580   16.9606   16.1418   15.2910   14.4082   13.4934   12.5466   11.5678
       10.5570    9.5142    8.4394    7.3326    6.1938    5.0230

    FINAL STATE:
    SAME STRUCTURE AS BEFORE
    1  OH X DOUBLET PI  GROUND STATE                    0  1  0  0  2
    0.9480871      0.650   3.500     0.005
     12          18.9108  39162.18                                     12
          0.00   1847.73   5417.37   8821.40  12061.76  15139.53  18054.80  20806.55
      23392.49  25808.94  28050.69  30110.87  31980.82  33649.91


       18.9108   18.5504   17.8387   17.1366   16.4411   15.7493   15.0581   14.3645
       13.6655   12.9581   12.2394   11.5063   10.7557    9.9849
    ```

    References:

    [AAA] Talks with Prof. Amaury Augusto de Almeida

    [BLB] Prof. Beatriz Leonor Barbuy

    [FCFcode] Fortran program that calculates the Franck-Condon factors
    """

    attrs = []

    def __init__(self):
        DataFile.__init__(self)

        self.states = [FCFInputState(), FCFInputState()]

    def from_molconsts(self, mc, maxv=None, ni=None, ns=None, igraph=None, ienerg=None, istate=None,
                       rmin=None, rmax=None, delr=None):
        """
        Calculates everything almost entirely based on a MolConsts object

        Information not present in mc may be passed as argument or let fall to same defaults as
        FCFInputState.

        Args:
            mc: MolConsts instance
            maxv:
            ni:
            ns:
            igraph:
            ienerg:
            istate:
            zmu:
            rmin:
            rmax:

        **Note**:  default to
                  FCFInputState defaults

        **Note**: kdmaxv is made = maxv
        """
        assert isinstance(mc, MolConsts)

        def get_state_obj(omega_e, omega_ex_e, alpha_e, be, label, mult, spdf):
            # formulas given by [AAA]
            de = omega_e ** 2 / 4 / omega_ex_e
            ev = [0.] + [omega_e * (v + .5) - omega_ex_e * (v + .5) ** 2 for v in range(maxv + 1)]
            bv = [be] + [be - alpha_e * (v + .5) for v in range(maxv + 1)]

            st = FCFInputState(
                title="{} {}".format(formula, state_to_str(label, mult, spdf, style=SS_PLAIN)),
                ni=ni, ns=ns, igraph=igraph, ienerg=ienerg, istate=istate,
                zmu=zmu,
                rmin=rmin, rmax=rmax, delr=delr,
                maxv=maxv,
                be=be,
                de=de,
                kdmaxv=kdmaxv,
                neig=neig,
                ev=ev,
                bv=bv,
            )
            return st

        default = FCFInputState()

        maxv = maxv if maxv is not None else default.maxv
        ni = ni if ni is not None else default.ni
        ns = ns if ns is not None else default.ns
        igraph = igraph if igraph is not None else default.igraph
        ienerg = ienerg if ienerg is not None else default.ienerg
        istate = istate if istate is not None else default.istate
        rmin = rmin if rmin is not None else default.rmin
        rmax = rmax if rmax is not None else default.rmax
        delr = delr if delr is not None else default.delr

        zmu = mc["am"]*mc["bm"]/(mc["am"]+mc["bm"])

        kdmaxv = maxv

        # "No continuum to be studied". To understand this, look for this quoted string in FCF486.FOR
        neig = 0

        formula = mc["formula"]


        st0 = get_state_obj(
            mc["statel_omega_e"],
            mc["statel_omega_ex_e"],
            mc["statel_alpha_e"],
            mc["statel_B_e"],
            mc["from_label"],
            mc["from_mult"],
            mc["from_spdf"],
        )

        st1 = get_state_obj(
            mc["state2l_omega_e"],
            mc["state2l_omega_ex_e"],
            mc["state2l_alpha_e"],
            mc["state2l_B_e"],
            mc["to_label"],
            mc["to_mult"],
            mc["to_spdf"],
        )

        self.states = [st0, st1]


    def _do_save_as(self, filename):
        with open(filename, "w") as h:
            self._write_state(h, self.states[0])
            self._write_state(h, self.states[1])

    def _write_state(self, h, st):
        h.write("{:50}{:3}{:3}{:3}{:3}{:3}\n".format(st.title, st.ni, st.ns, st.igraph, st.ienerg, st.istate))
        h.write("{:10g}{:10g}{:10g}{:10.3}\n".format(st.zmu, st.rmin, st.rmax, st.delr))
        h.write("{:3}{:7}{:10g}{:10g}{:36}{:3}\n".format(st.maxv, "", st.be, st.de, "", st.kdmaxv, st.neig))
        for i in range(4):
            h.write("".join("{:10g}".format(x) for x in st.ev[i*8:(i+1)*8])+"\n")
        for i in range(4):
            h.write("".join("{:10g}".format(x) for x in st.bv[i*8:(i+1)*8])+"\n")

    def _do_load(self, filename):
        with open(filename, "r") as h:
            self._read_state(h, self.states[0])
            self._read_state(h, self.states[1])

    def _read_state(self, h, st):

        def read32(h):
            """Used to read ev[] and bv[]. 4*8 values expected, but maybe not all present"""
            _ret = []
            for _ in range(4):
                _ret.extend(a99.str_vector(h))

            ret = [tfloat(x) for x in _ret]
            return ret

        # # Each "block" of information read is preceded by a sample of what needs to be read

        # 1  OH A DOUBLET SIGMA UPPER STATE                   0  1  0  0  2
        line = h.readline()
        assert isinstance(st, FCFInputState)
        st.title = line[0:50]
        st.ni = tint(line[50:53])
        st.ns = tint(line[53:56])
        st.igraph = tint(line[56:59])
        st.ienerg = tint(line[59:62])
        st.istate = tint(line[62:65])

        # 0.9480871     0.750     3.500     0.005
        #
        line = h.readline()
        st.zmu = tfloat(line[0:10])
        st.rmin = tfloat(line[10:20])
        st.rmax = tfloat(line[20:30])
        st.delr = tfloat(line[30:40])

        #  12           17.358  35000.00                                     12
        line = h.readline()
        st.maxv = tint(line[0:3])
        st.be = tfloat(line[10:20])
        st.de = tfloat(line[20:30])
        st.kdmaxv = tint(line[66:69])
        st.neig = tint(line[69:72])

        #      00.00   1565.99   4554.82   7351.07   9959.53  12392.75  14671.06  16822.54
        #   18883.03  20896.17  22913.33  24993.67  27204.10  29619.32
        #
        #
        st.ev = read32(h)
        #    17.3580   16.9606   16.1418   15.2910   14.4082   13.4934   12.5466   11.5678
        #    10.5570    9.5142    8.4394    7.3326    6.1938    5.0230
        #
        #
        st.bv = read32(h)


def tolerant(string, type_):
    """Tolerant int or float: empty string falls back to zero"""
    try:
        return type_(string)
    except ValueError:
        if len(string.strip()) == 0:
            return type_(0)
        raise


def tint(string):
    return tolerant(string, int)


def tfloat(string):
    return tolerant(string, float)

