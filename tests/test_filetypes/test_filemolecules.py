import os
import f311.filetypes as ft



def test_SetOfLines():
    sol = ft.SetOfLines()
    sol.append_line(2000., .25, 10.5, "P")
    sol.append_line(1000., .25, 10.5, "Q1")

    assert sol.llzero == 1000.
    assert sol.llfin  == 2000.
    assert sol.num_lines == 2
    assert len(sol) == 2


    assert sol.lmbdam[0] == 2000.

    sol.sort()

    assert sol.lmbdam[0] == 1000.

    sol.cut(500, 1500)


    assert sol.llzero == 1000.
    assert sol.llfin  == 1000.
    assert sol.num_lines == 1
    assert len(sol) == 1

    sol.sort()


def test_Molecule():
    m = ft.Molecule()

    sol = ft.SetOfLines()
    sol.append_line(2000., .25, 10.5, "P")
    sol.append_line(1000., .25, 10.5, "Q1")

    m.sol = [sol]


    assert m.llzero == 1000.
    assert m.llfin == 2000.
    assert m.num_lines == 2


    sol = ft.SetOfLines()
    sol.append_line(3000., .125, 13.5, "R21")

    m.sol.append(sol)

    assert len(m) == 2
    assert m.num_lines == 3

    assert all(m.lmbdam == [2000., 1000., 3000.])
    assert all(m.sj == [.25, .25, .125])
    assert all(m.jj == [10.5, 10.5, 13.5])
    assert all(m.branch == ["P", "Q1", "R21"])


    m.qqv
    m.ggv
    m.bbv
    m.ddv

    m.cut(500, 1500)

    assert m.num_lines == 1



def test_FileMolecules(tmpdir):
    os.chdir(str(tmpdir))
    m = ft.Molecule()
    sol = ft.SetOfLines()
    sol.append_line(2000., .25, 10.5, "P")
    sol.append_line(1000., .25, 10.5, "Q1")
    m.sol = [sol]
    sol = ft.SetOfLines()
    sol.append_line(3000., .125, 13.5, "R21")
    m.sol.append(sol)


    f = ft.FileMolecules()
    f.molecules = [m]

    assert f.llzero == 1000.
    assert f.llfin == 3000.
    assert f.num_lines == 3
    assert f.num_sols == 2

    f.lmbdam
    f.sj
    f.jj
    f.branch
    f.qqv
    f.ggv
    f.bbv
    f.ddv
    f.fe
    f.do
    f.mm
    f.am
    f.ua
    f.ub
    f.te
    f.cro
    f.s

    f.cut(500, 1500)

    assert f.num_lines == 1
    assert f.num_sols == 1

    m.symbols = ["We", "Ur"]

    assert m.formula == "WeUr"

    f.save_as("qq")

def test_molconsts_to_molecule(tmpdir):
    os.chdir(str(tmpdir))
    db = ft.FileMolDB()
    db.init_default()

    mc = ft.some_molconsts(db)

    mm = ft.molconsts_to_molecule(mc)
