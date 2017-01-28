from f311 import physics as ph
import tabulate


def test_get_ubv_bandpasses():
    _ = ph.get_ubv_bandpasses()


def test_get_ubv_bandpasses_dict():
    _ = ph.get_ubv_bandpasses_dict()


def test_get_ubv_bandpass():
    for name in "UBVRI":
        _ = ph.get_ubv_bandpass(name)


def test_calc_mag():
    systems = ["stdflux", "ab", "vega"]
    bands = "UBVRIJHK"
    sp = ph.get_vega_spectrum()
    rows = [([band]+[ph.calc_mag(sp, band, system) for system in systems]) for band in bands]
    assert tabulate.tabulate(rows, ["band"]+systems) == \
"""band        stdflux          ab    vega
------  -----------  ----------  ------
U        0.00572505   0.761594       -0
B        0.0696287   -0.10383        -0
V        0.0218067    0.0191189      -0
R        0.0359559    0.214645       -0
I        0.0661095    0.449825       -0
J       -0.0150993    0.874666       -0
H        0.0315447    1.34805        -0
K        0.0246046    1.85948        -0"""

