import f311.pyfant as pf
import os
import glob


# Note: requires PFANT installed


def test_copy_star(tmpdir):
    os.chdir(str(tmpdir))

    dir_ = os.path.join(pf.get_pfant_data_path(), 'arcturus')
    pf.copy_star(dir_)

    assert glob.glob("*") == ['abonds.dat', 'main.dat']


def test_link_to_data(tmpdir):
    os.chdir(str(tmpdir))
    pf.link_to_data(pf.get_pfant_data_path("common"))
    d = glob.glob("*")
    d.sort()
    assert d == ['absoru2.dat', 'atoms.dat', 'grid.mod', 'grid.moo', 'hmap.dat', 'molecules.dat', 'partit.dat']


def test_run_combo(tmpdir):
    os.chdir(str(tmpdir))
    pf.copy_star(pf.get_pfant_data_path('arcturus'))
    pf.link_to_data(pf.get_pfant_data_path("common"))
    c = pf.Combo()
    c.run()


def test_run_parallel(tmpdir):
    os.chdir(str(tmpdir))

    pf.copy_star(pf.get_pfant_data_path('arcturus'))
    pf.link_to_data(pf.get_pfant_data_path("common"))

    cc = []

    c = pf.Combo()
    c.conf.flag_output_to_dir = True
    cc.append(c)
    c = pf.Combo()
    c.conf.flag_output_to_dir = True
    cc.append(c)

    pf.run_parallel(cc, flag_console=False)


def test_setup_inputs(tmpdir):
    os.chdir(str(tmpdir))

    pf.setup_inputs()

    d = glob.glob("*")
    d.sort()

    assert d == ['abonds.dat', 'absoru2.dat', 'atoms.dat', 'grid.mod', 'grid.moo', 'hmap.dat',
                 'main.dat', 'molecules.dat', 'partit.dat']

