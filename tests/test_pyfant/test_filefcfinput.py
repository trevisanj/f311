import f311.filetypes as ft
import os

_STREAM = """1  NH A TRIPLET PI UPPER STATE                      0  1  0  0  2
0.94901603     0.750     3.500     0.005
 12          16.6745  29609.42                                     12
     00.00   1590.95   4624.95   7461.75  10101.35  12543.75  14788.95  16836.95
  18687.75  20341.35  21797.75  23056.95  24118.95  24983.75


   16.6745   16.3018   15.5564   14.8110   14.0656   13.3202   12.5748   11.8294
   11.0840   10.3386    9.5932    8.8478    8.1024    7.3570


1  NH X TRIPLET SIGMA  GROUND STATE                 0  1  0  0  2
0.94901603     0.750     3.500     0.005
 12          16.6993  29609.42                                     12
      0.00   1621.51   4747.01   7715.81  10527.91  13183.31  15682.01  18024.01
  20209.31  22237.91  24109.81  25825.01  27383.51  28785.31


   16.6993   16.3748   15.7258   15.0768   14.4278   13.7788   13.1298   12.4808
   11.8318   11.1828   10.5338    9.8848    9.2358    8.5868



"""


def test_load(tmpdir):
    os.chdir(str(tmpdir))
    filename = "abacate"
    with open(filename, "w") as f:
        f.write(_STREAM)

    f = ft.FileTRAPRBInput()
    f.load(filename)

    assert f.states[0].__dict__ == \
        ft.TRAPRBInputState(title='1  NH A TRIPLET PI UPPER STATE                    ', ni=0, ns=1, igraph=0, ienerg=0, istate=2, zmu=0.94901603, rmin=0.75, rmax=3.5, delr=0.005, maxv=12, be=16.6745, de=29609.42, kdmaxv=12, neig=0, ev=[0.0, 1590.95, 4624.95, 7461.75, 10101.35, 12543.75, 14788.95, 16836.95, 18687.75, 20341.35, 21797.75, 23056.95, 24118.95, 24983.75], bv=[16.6745, 16.3018, 15.5564, 14.811, 14.0656, 13.3202, 12.5748, 11.8294, 11.084, 10.3386, 9.5932, 8.8478, 8.1024, 7.357]).__dict__

    assert f.states[1].__dict__ == \
        ft.TRAPRBInputState(title='1  NH X TRIPLET SIGMA  GROUND STATE               ', ni=0, ns=1, igraph=0, ienerg=0, istate=2, zmu=0.94901603, rmin=0.75, rmax=3.5, delr=0.005, maxv=12, be=16.6993, de=29609.42, kdmaxv=12, neig=0, ev=[0.0, 1621.51, 4747.01, 7715.81, 10527.91, 13183.31, 15682.01, 18024.01, 20209.31, 22237.91, 24109.81, 25825.01, 27383.51, 28785.31], bv=[16.6993, 16.3748, 15.7258, 15.0768, 14.4278, 13.7788, 13.1298, 12.4808, 11.8318, 11.1828, 10.5338, 9.8848, 9.2358, 8.5868]).__dict__


_STREAM2 = """1  OH A DOUBLET SIGMA UPPER STATE                   0  1  0  0  2
  0.948087      0.75       3.5     0.005
 12           17.358     35000                                     12
         0   1565.99   4554.82   7351.07   9959.53   12392.8   14671.1   16822.5
     18883   20896.2   22913.3   24993.7   27204.1   29619.3


    17.358   16.9606   16.1418    15.291   14.4082   13.4934   12.5466   11.5678
    10.557    9.5142    8.4394    7.3326    6.1938     5.023


1  OH X DOUBLET PI  GROUND STATE                    0  1  0  0  2
  0.948087      0.65       3.5     0.005
 12          18.9108   39162.2                                     12
         0   1847.73   5417.37    8821.4   12061.8   15139.5   18054.8   20806.5
   23392.5   25808.9   28050.7   30110.9   31980.8   33649.9


   18.9108   18.5504   17.8387   17.1366   16.4411   15.7493   15.0581   14.3645
   13.6655   12.9581   12.2394   11.5063   10.7557    9.9849


"""

def test_load_save_load(tmpdir):
    os.chdir(str(tmpdir))
    filename = "abacate"
    with open(filename, "w") as f:
        f.write(_STREAM2)

    f = ft.FileTRAPRBInput()
    f.load(filename)

    f.save_as("guarana")

    g = ft.FileTRAPRBInput()
    g.load("guarana")

    assert f.states[0].__dict__ == g.states[0].__dict__
    assert f.states[1].__dict__ == g.states[1].__dict__


def test_from_molconsts(tmpdir):
    os.chdir(str(tmpdir))
    mc = ft.some_molconsts()

    f = ft.FileTRAPRBInput()
    f.from_molconsts(mc, 15)
