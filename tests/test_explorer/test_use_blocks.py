import os
import f311.explorer as ex
import f311.filetypes as ft
import a99
from astropy import units as u
import numpy as np
import f311.physics as ph


def get_spectrum():
    sp = ft.Spectrum()
    sp.x = np.linspace(5000, 5100, 100)
    sp.y = np.random.random(100)+2.
    sp.filename = "random"
    return sp

def get_spectrum_list():
    sl = ft.SpectrumList()
    for i in range(3):
        sl.add_spectrum(get_spectrum())
    return sl


def test_use_GB_SNR():
    sl = get_spectrum_list()
    blk = ex.GB_SNR()
    out = blk.use(sl)


def test_use_GB_UseNumPyFunc():
    sl = get_spectrum_list()
    blk = ex.GB_UseNumPyFunc(np.sum)
    out = blk.use(sl)


def test_use_SB_Add():
    sp = get_spectrum()
    blk = ex.SB_Add(2.)
    out = blk.use(sp)


def test_use_SB_AddNoise():
    sp = get_spectrum()
    blk = ex.SB_AddNoise()
    out = blk.use(sp)


def test_use_SB_ConvertYUnit():
    sp = get_spectrum()
    blk = ex.SB_ConvertYUnit(ph.flambda)
    out = blk.use(sp)


def test_use_SB_Cut():
    sp = get_spectrum()
    blk = ex.SB_Cut(5000, 5050)
    out = blk.use(sp)


def test_use_SB_DivByLambda():
    sp = get_spectrum()
    blk = ex.SB_DivByLambda()
    out = blk.use(sp)


def test_use_SB_ElementWise():
    sp = get_spectrum()
    blk = ex.SB_ElementWise(lambda x: x+1)
    out = blk.use(sp)


def test_use_SB_Extend():
    sp = get_spectrum()
    blk = ex.SB_Extend()
    out = blk.use(sp)


def test_use_SB_FLambdaToFNu():
    sp = get_spectrum()
    blk = ex.SB_FLambdaToFNu()
    out = blk.use(sp)


def test_use_SB_FNuToFlambda():
    sp = get_spectrum()
    blk = ex.SB_FNuToFlambda()
    out = blk.use(sp)


def test_use_SB_Mul():
    sp = get_spectrum()
    blk = ex.SB_Mul(2.)
    out = blk.use(sp)


def test_use_SB_MulByLambda():
    sp = get_spectrum()
    blk = ex.SB_MulByLambda()
    out = blk.use(sp)


def test_use_SB_Normalize():
    sp = get_spectrum()
    blk = ex.SB_Normalize()
    out = blk.use(sp)


def test_use_SB_Rubberband():
    sp = get_spectrum()
    blk = ex.SB_Rubberband()
    out = blk.use(sp)


def test_use_SLB_ExtractContinua():
    sl = get_spectrum_list()
    blk = ex.SLB_ExtractContinua()
    out = blk.use(sl)


def test_use_SLB_UseSpectrumBlock():
    sl = get_spectrum_list()
    blk = ex.SLB_UseSpectrumBlock(ex.SB_Rubberband())
    out = blk.use(sl)


def test_use_ToScalar_Magnitude():
    sp = get_spectrum()
    blk = ex.ToScalar_Magnitude("B")
    out = blk.use(sp)


def test_use_ToScalar_SNR():
    sp = get_spectrum()
    blk = ex.ToScalar_SNR(5000,5100)
    out = blk.use(sp)


def test_use_ToScalar_UseNumPyFunc():
    sp = get_spectrum()
    blk = ex.ToScalar_UseNumPyFunc(np.sum)
    out = blk.use(sp)

