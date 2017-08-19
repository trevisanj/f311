import f311.filetypes as ft


_KEYS = ["fe", "bm", "te", "do", "ua", "cro", "am", "ub", "s",
         "from_label", "to_label", "from_spdf", "to_spdf",
         "statel_omega_e", "statel_B_e", "statel_beta_e", "statel_omega_ex_e", "statel_alpha_e",
         "statel_A", "statel_omega_ey_e", "statel_D_e",
         "state2l_omega_e", "state2l_B_e", "state2l_beta_e", "state2l_omega_ex_e", "state2l_alpha_e",
         "state2l_A", "state2l_omega_ey_e", "state2l_D_e",]



class MolConsts(dict):
    """Dict subclass that will hold several molecular constants

    The dictionary keys match field names in tables ("pfantmol", "state", "system") in a FileMolDB.
    Keys "statel_*" and "state2l_*" have these prefixes to indicate initial and final state.

    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

        for key in _KEYS:
            self[key] = None


    def populate_from_db(self, db, idpfantmol, idsystem, idstatel, idstate2l):
        """
        Assembles a MolConsts object containig information specified by arguments

        Args:
            idpfantmol: id in table "pfantmol"
            idsystem: id in table "system"
            idstatel: id in table "state" for the initial state
            idstate2l: id in table "state" for the final state

        TODO: idstatel, idstate2l are redundant: this could be retrieved from the system (check if there are repetitions in the NIST table). Paramneters may be optional. I could use the same _map, but update it manually if (statel, state2l) not passed
        """
        assert isinstance(db, ft.FileMolDB)

        # id, table name, prefix for key in dictionary
        _map = [(idpfantmol, "pfantmol", ""),
                (idsystem, "system", ""),
                (idstatel, "state", "statel_"),
                (idstate2l, "state", "state2l_")]

        for id_, tablename, prefix in _map:
            ti = db.get_table_info(tablename)
            row = db.get_conn().execute("select * from {} where id = ?".format(tablename), (id_,)).fetchone()
            for fieldname in ti:
                if not fieldname.startswith("id"):
                    self[prefix + fieldname] = row[fieldname]


