import aosss as ao
import numpy as np
import astropy.units as u


def test_BulkItem():
    obj = ao.BulkItem()


def test_FileFullCube():
    obj = ao.FileFullCube()


def test_FilePar():
    obj = ao.FilePar()


def test_FileSparseCube():
    obj = ao.FileSparseCube()


def test_FileSpectrumList():
    obj = ao.FileSpectrumList()


def test_FullCube():
    obj = ao.FullCube()


def test_GB_SNR():
    obj = ao.GB_SNR()


def test_GB_UseNumPyFunc():
    obj = ao.GB_UseNumPyFunc()


def test_GroupBlock():
    obj = ao.GroupBlock()


def test_SB_Add():
    obj = ao.SB_Add()


def test_SB_AddNoise():
    obj = ao.SB_AddNoise()


def test_SB_ConvertYUnit():
    obj = ao.SB_ConvertYUnit(u.hertz)


def test_SB_Cut():
    obj = ao.SB_Cut(1000, 2000)


def test_SB_DivByLambda():
    obj = ao.SB_DivByLambda()


def test_SB_ElementWise():
    obj = ao.SB_ElementWise(np.sqrt)


def test_SB_Extend():
    obj = ao.SB_Extend()


def test_SB_FLambdaToFNu():
    obj = ao.SB_FLambdaToFNu()


def test_SB_FnuToFlambda():
    obj = ao.SB_FnuToFlambda()


def test_SB_Mul():
    obj = ao.SB_Mul()


def test_SB_MulByLambda():
    obj = ao.SB_MulByLambda()


def test_SB_Normalize():
    obj = ao.SB_Normalize()


def test_SB_Rubberband():
    obj = ao.SB_Rubberband()


def test_SLB_ExtractContinua():
    obj = ao.SLB_ExtractContinua()


def test_SLB_UseSpectrumBlock():
    obj = ao.SLB_UseSpectrumBlock()


def test_SparseCube():
    obj = ao.SparseCube()


def test_SpectrographMode():
    obj = ao.SpectrographMode()


def test_SpectrumBlock():
    obj = ao.SpectrumBlock()


def test_SpectrumCollection():
    obj = ao.SpectrumCollection()


def test_SpectrumList():
    obj = ao.SpectrumList()


def test_SpectrumListBlock():
    obj = ao.SpectrumListBlock()


def test_ToScalar():
    obj = ao.ToScalar()


def test_ToScalar_Magnitude():
    obj = ao.ToScalar_Magnitude("U")


def test_ToScalar_SNR():
    obj = ao.ToScalar_SNR(0, 10000)


def test_ToScalar_UseNumPyFunc():
    obj = ao.ToScalar_UseNumPyFunc()


def test_VisCube():
    obj = ao.VisCube()


def test_VisSpectrumList():
    obj = ao.VisSpectrumList()

