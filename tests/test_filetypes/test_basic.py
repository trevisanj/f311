import f311.filetypes as ft

def test_greek_to_spdf():
    tt = [ft.greek_to_spdf(x) for x in ft.basic._SPDF_TO_GREEK.values()]
    assert(tt == list(ft.basic._GREEK_TO_SPDF.values()))


def test_spdf_to_greek():
    tt = [ft.spdf_to_greek(x) for x in range(len(ft.basic._SPDF_TO_GREEK))]
    assert(tt == list(ft.basic._SPDF_TO_GREEK.values()))
