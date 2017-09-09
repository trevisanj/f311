from f311 import filetypes as ft
from f311 import physics as ph
import os

def test_populate_from_db(tmpdir):
    os.chdir(str(tmpdir))
    db = ft.FileMolDB()
    db.init_default()

    consts = ph.MolConsts()
    consts.populate_from_db(db, id_system=6, id_pfantmol=12, id_statel=96, id_state2l=97)