import f311.filetypes as ft

def test_populate_molconsts():
    c = ft.MolConsts()
    f = ft.FileMolDB()
    f.init_default()
    c.populate_parse_str(f, "OH [A 2 SIGMA - X 2 PI]")
    c.populate_ids(f)
