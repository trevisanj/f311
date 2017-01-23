import f311.pyfant as pf
import os
import io


def _fake_file():
    """Returns StringIO file to test FileVald3 class"""

    f = io.StringIO()
    f.write("""  204.5126 -7.917  2.5    83.925  2.5  48964.990 108X00f1   A07e1   16
  204.7561 -7.745  3.5   202.380  3.5  49025.320 108X00f1   A07e1   16
  204.9400 -7.883  5.5   543.596  6.5  49322.740 108X00e1   A07e1   16
  205.0076 -7.931  3.5   201.931  2.5  48964.990 108X00e1   A07e1   16
  205.0652 -7.621  4.5   355.915  4.5  49105.280 108X00f1   A07e1   16
""")

    f.seek(0)
    return f


def test_filemolkurucz():
    h = _fake_file()
    f = pf.FileKuruczMolecule()
    f._do_load_h(h, "_fake_file")
    assert repr(f.lines[0]) == "KuruczMolLine(2045.126, -7.917, 2.5, 83.925, 2.5, 48964.99, 1, 8, 'X', 0, 'f', 1, 'A', 7, 'e', 1, 6)"


def test_conv_kurucz(tmpdir):
    pass
    os.chdir(str(tmpdir))
    db = pf.FileMolDB()
    db.init_default()
    # conn = db.get_conn()
    mol_row = db.query_molecule(id=7).fetchone()  # supposed to be OH
    state_row = db.query_state(**{"state.id": 97}).fetchone()  # supposed to be "X ²Pi_i"

    h = _fake_file()
    fileobj = pf.FileKuruczMolecule()
    fileobj._do_load_h(h, "_fake_file")

    sols, log = pf.convmol.kurucz_to_sols(mol_row, state_row, fileobj,
        pf.convmol.calc_qgbd_tio_like, flag_hlf=True, flag_fcf=True)
