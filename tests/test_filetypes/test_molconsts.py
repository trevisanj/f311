import pytest
from f311 import filetypes as ft
import os

def test_populate_all_using_ids(tmpdir):
    os.chdir(str(tmpdir))
    db = ft.FileMolDB()
    db.init_default()

    consts = ft.MolConsts()
    consts.populate_all_using_ids(db, id_molecule=7, id_system=6, id_pfantmol=12, id_statel=96, id_state2l=97)

def test_populate_all_using_ids_raises(tmpdir):
    """Uses invalid ids to see method raising ValueError"""
    os.chdir(str(tmpdir))
    db = ft.FileMolDB()
    db.init_default()

    consts = ft.MolConsts()
    with pytest.raises(ValueError):
        consts.populate_all_using_ids(db, id_molecule=111, id_system=11116, id_pfantmol=11112, id_statel=111196, id_state2l=111197)

def test_populate_parse_str():
    consts = ft.MolConsts()
    consts.populate_parse_str("MgH [A 2 sigma - x 3 pi]")
    assert(consts["formula"] == "MgH")
    assert(consts["from_label"] == "A" and consts["from_mult"] == 2 and consts["from_spdf"] == 0)
    assert(consts["to_label"] == "x" and consts["to_mult"] == 3 and consts["to_spdf"] == 1)


def test_populate_all_using_str(tmpdir):
    os.chdir(str(tmpdir))
    db = ft.FileMolDB()
    db.init_default()

    consts = ft.MolConsts()
    consts.populate_all_using_str(db, "OH [A 2 SIGMA - X 2 PI]")


def test_parse_pfantmol_descriptions(tmpdir):
    os.chdir(str(tmpdir))
    db = ft.FileMolDB()
    db.init_default()


    cursor = db.get_conn().execute("select * from pfantmol")
    for row in cursor:
        mc = ft.MolConsts()
        mc.populate_parse_str(row["description"])
