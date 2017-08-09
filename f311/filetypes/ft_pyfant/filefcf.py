__all__ = ["FileFCF"]

from .. import DataFile
from collections import OrderedDict
import re
import a99

class FileFCF(DataFile):
    """
    File containing Franck-Condon Factors (FCFs)

    Usage: attribute "fcfs" is a dictionary accessed by key (vl, v2l)

    **History:**

    This file is the output of the Fortran code that calculated FCFs for Bruno Castilho's thesis.

    In 2015, I modified this Fortran code to compile with gfortran on request from
    Prof. Amaury Augusto de Almeida, but I believe that the code remains unpublished.

    Nevertheless, Bruno left several output files in his directory ATMOS:/wrk4/bruno/Mole/Fc
    containing tabulated FCFs for several molecules. The reason why I created this class is to read
    these files.
    """

    attrs = ["fcfs"]

    @property
    def num_lines(self):
        return len(self)

    def __len__(self):
        return len(self.fcfs)

    def __getitem__(self, item):
        return self.fcfs[item]

    def __init__(self):
        DataFile.__init__(self)

        self.fcfs = OrderedDict()


    def _do_load(self, filename):
        # File part of interest looks like this:

        #                                 V"   V""  FRANCK CONDON FACTOR     R-CENTROID
        #
        #                                  0   0    .8809749E+00             .1159111E+01
        #                                  0   1    .6597226E-01             .1573085E+01
        #                                  0   2    .4967269E-01             .1309538E+01
        #                                  0   3    .4893512E-06             .5487973E+02
        #                                  0   4    .1967671E-02             .1092197E+01
        #                                  0   5    .5098846E-03             .7344212E+00
        #                                  0   6    .3264353E-03             .8154120E+00
        #                                  0   7    .1959470E-03             .8020893E+00
        #                                  0   8    .1221533E-03             .7933001E+00
        #                                  0   9    .7849922E-04             .7871405E+00
        #                                  0  10    .5130633E-04             .7806426E+00
        #
        #                                 V"   V""  FRANCK CONDON FACTOR     R-CENTROID
        #
        #                                  1   0    .7950073E-01             .9007177E+00
        #                                  1   1    .7301335E+00             .1176593E+01
        #                                  1   2    .5329854E-01             .1873632E+01
        #                                  1   3    .1172008E+00             .1293195E+01
        #                                  1   4    .9687749E-03            -.1106724E+01
        #                                  1   5    .8699398E-02             .1027710E+01
        #                                  1   6    .3409328E-02             .7787252E+00
        #                                  1   7    .2211213E-02             .8098937E+00
        #                                  1   8    .1418452E-02             .8016906E+00
        #                                  1   9    .9225228E-03             .7913423E+00
        #                                  1  10    .6110833E-03             .7833238E+00
        # 1
        #
        #                                 V"   V""  FRANCK CONDON FACTOR     R-CENTROID
        #
        #                                  2   0    .1939492E-01             .1045730E+01
        #                                  2   1    .4528844E-01             .1349549E+01
        #                                  2   2    .1031371E+00             .1003365E+01
        #                                  2   3    .4823686E+00             .1247711E+01
        #                                  2   4    .7587573E-01             .2082369E+01
        #                                  2   5    .2123286E+00             .1379030E+01
        #                                  2   6    .2887595E-02            -.1045935E+01
        #                                  2   7    .1985530E-01             .9975332E+00
        #                                  2   8    .1103128E-01             .8153041E+00
        #                                  2   9    .7418684E-02             .8001242E+00
        #                                  2  10    .5176848E-02             .7976580E+00
        #

        # magic characters
        MAGIC = 'V"   V""  FRANCK CONDON FACTOR     R-CENTROID'

        # possible states for parsing file
        EXP_MAGIC = 0 # Expecting magic characters
        EXP_BLANK = 1 # Expecting blank line
        EXP_DATA = 2 # Expecting data, "1*" or blank line

        # regular expression for extraction the data
        rec = re.compile("\s*(\d+)\s*(\d+)\s*([\deE\.\+\-]+)")


        with open(filename, "r") as h:
            found = False
            state = EXP_MAGIC
            i = 0
            try:
                for line in h:
                    i += 1
                    if state == EXP_MAGIC:
                       if line.strip() == MAGIC:
                           state = EXP_BLANK
                           found = True

                    elif state == EXP_BLANK:
                        if line.strip() == "":
                            state = EXP_DATA
                    elif state == EXP_DATA:
                        if line.strip() == "" or line[0] == "1":
                            state = EXP_MAGIC
                        else:
                            m = rec.match(line)
                            if m is None:
                                raise RuntimeError("Could not extract (vl, v2l, fcf)")
                            vl, v2l, fcf = m.groups()
                            vl = int(vl)
                            v2l = int(v2l)

                            if (vl, v2l) in self.fcfs:
                                a99.get_python_logger().warning("Repeated (vl, v2l): ({}, {})".format(vl, v2l))

                            fcf = float(fcf)
                            self.fcfs[(vl, v2l)] = fcf
            except Exception as e:
                raise RuntimeError("Error in line {}".format(i)) from e


            if not found:
                raise RuntimeError("File does not appear to be a FileFCF")

