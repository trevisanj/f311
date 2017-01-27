import f311.explorer as ex
import a99
from astropy import units as u

def test_GB_SNR():
    _ = ex.GB_SNR()


def test_GB_UseNumPyFunc():
    _ = ex.GB_UseNumPyFunc()


def test_GroupBlock():
    _ = ex.GroupBlock()


def test_PlotSpectrumSetup():
    _ = ex.PlotSpectrumSetup()


def test_SB_Add():
    _ = ex.SB_Add()


def test_SB_AddNoise():
    _ = ex.SB_AddNoise()


def test_SB_ConvertYUnit():
    _ = ex.SB_ConvertYUnit(u.Jy)


def test_SB_Cut():
    _ = ex.SB_Cut(5000, 6000)


def test_SB_DivByLambda():
    _ = ex.SB_DivByLambda()


def test_SB_ElementWise():
    _ = ex.SB_ElementWise(lambda x: x-1)


def test_SB_Extend():
    _ = ex.SB_Extend()


def test_SB_FLambdaToFNu():
    _ = ex.SB_FLambdaToFNu()


def test_SB_FnuToFlambda():
    _ = ex.SB_FnuToFlambda()


def test_SB_Mul():
    _ = ex.SB_Mul()


def test_SB_MulByLambda():
    _ = ex.SB_MulByLambda()


def test_SB_Normalize():
    _ = ex.SB_Normalize()


def test_SB_Rubberband():
    _ = ex.SB_Rubberband()


def test_SLB_ExtractContinua():
    _ = ex.SLB_ExtractContinua()


def test_SLB_UseSpectrumBlock():
    _ = ex.SLB_UseSpectrumBlock()


def test_SpectrumBlock():
    _ = ex.SpectrumBlock()


def test_SpectrumListBlock():
    _ = ex.SpectrumListBlock()


def test_ToScalar():
    _ = ex.ToScalar()


def test_ToScalar_Magnitude():
    _ = ex.ToScalar_Magnitude("U")


def test_ToScalar_SNR():
    _ = ex.ToScalar_SNR(0, 100000)


def test_ToScalar_UseNumPyFunc():
    _ = ex.ToScalar_UseNumPyFunc()


def test_XExplorer():
    app = a99.get_QApplication()
    form = ex.XExplorer(_flag_set_dir=False)

def test_XHTML():
    app = a99.get_QApplication()
    _ = ex.XHTML()


def test_XText():
    app = a99.get_QApplication()
    _ = ex.XText()

