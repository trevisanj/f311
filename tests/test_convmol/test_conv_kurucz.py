import os
import io
import f311.filetypes as ft
import f311.convmol as cm
import f311.physics as ph


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
    f = ft.FileKuruczMolecule()
    f._do_load_h(h, "_fake_file")
    assert repr(f.lines[0]) == "KuruczMolLine(lambda_=2045.126, loggf=-7.917, J2l=2.5, E2l=83.925, Jl=2.5, El=48964.99, atomn0=1, atomn1=8, state2l='X', v2l=0, lambda_doubling2l='f', spin2l=1, statel='A', vl=7, lambda_doublingl='e', spinl=1, iso=16)"


def test_conv_kurucz(tmpdir):
    pass
    os.chdir(str(tmpdir))

    db = ft.FileMolDB()
    db.init_default()
    # conn = db.get_conn()


    molconsts = ft.MolConsts()
    molconsts.populate_all_using_str(db, "OH [A 2 Sigma - X 2 Pi]")
    molconsts.None_to_zero()

    h = _fake_file()
    fileobj = ft.FileKuruczMolecule()
    fileobj._do_load_h(h, "_fake_file")

    conv = cm.ConvKurucz(molconsts=molconsts,
                         flag_hlf=True, flag_normhlf=True, flag_fcf=False, flag_quiet=False,
                         fcfs=None, iso=None)

    f, log = conv.make_file_molecules(fileobj)

    assert f.num_lines == 5
    assert f[0].s == 0.5