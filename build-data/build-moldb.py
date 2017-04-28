#!/usr/bin/env python3
"""
Script to put together the file moldb.sqlite
"""

from f311 import filetypes as ft
import f311.convmol as cm
import a99
from collections import OrderedDict
import sqlite3
import os
import sys
from f311 import convmol as cm

# Molecules present in PFANT molecules.dat
MOLECULES = [("MgH", "Magnesium monohydride"),
             ("C2", "Dicarbon"),
             ("CN", "Cyano radical"),
             ("CH", "Methylidyne"),
             ("NH", "Imidogen"),
             ("CO", "Carbon monoxide"),
             ("OH", "Hydroxyl radical"),
             ("FeH", "Iron hydride"),
             ("TiO", "Titanium oxide")]


# TODO reshape this. Actually I think that this thing should move to build-moldb.py
def insert_molecules(moldb):
    """Tries to download data from NIST Web Book online"""
    assert isinstance(moldb, ft.FileMolDB)
    from f311 import convmol as cm

    conn = moldb.get_conn()


    for formula, name in MOLECULES:
        try:
            data, _, name = cm.get_nist_webbook_constants(formula)

            fe, do, am, bm, ua, ub, te, cro, s = None, None, None, None, None, None, None, None, \
                                                 None

            # Tries to retrieve "fe", "do" etc from molecules.dat
            symbols = ft.description_to_symbols(formula)
            if not symbols:
                a99.get_python_logger().warning("Formula '{}' not in internal BUILTIN_FORMULAS, "
                                                "and probably this molecule is also not in PFANT/data/common/molecules.dat".
                                                format(formula))

                symbols = ["", ""]
            else:
                m = bysym.get(tuple(symbols))
                if m:
                    fe = m.fe
                    do = m.do
                    am = m.am
                    bm = m.bm
                    ua = m.ua
                    ub = m.ub
                    te = m.te
                    cro = m.cro
                    s = m.s

            symbols = [x.strip() for x in symbols]
            conn.execute("insert into molecule "
                         "(formula, name, symbol_a, symbol_b, fe, do, am, bm, ua, ub, te, cro, s) "
                         "values (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         (
                         formula, name, symbols[0], symbols[1], fe, do, am, bm, ua, ub, te, cro, s))

            id_molecule = conn.execute("select last_insert_rowid() as id").fetchone()["id"]
            for state in data:
                # **Note** assumes that the columns in data match the
                # (number of columns in the state table - 2) and their order
                conn.execute("insert into state values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                             [None, id_molecule] + state)

            conn.commit()

        except:
            a99.get_python_logger().exception("Failed for molecule '{}'".format(formula))

    conn.close()



















# TODO reshape this. Actually I think that this thing should move to build-moldb.py
def insert_nist_data(moldb):
    """Tries to download data from NIST Web Book online"""
    assert isinstance(moldb, ft.FileMolDB)

    conn = moldb.get_conn()
    # TODO gather more formulae
    formulae = ["MgH", "C2", "CN", "CH", "NH", "CO", "OH", "FeH", "TiO"]

    # Uses PFANT/data/common/molecules.dat to retrieve "fe", "do", "am", etc.
    filemol = ft.FileMolecules()
    filemol.load(pf.get_pfant_data_path("common", "molecules.dat"))
    bysym = dict([(tuple(m.symbols), m) for m in filemol])

    for formula in formulae:
        try:
            data, _, name = cm.get_nist_webbook_constants(formula)

            fe, do, am, bm, ua, ub, te, cro, s = None, None, None, None, None, None, None, None, \
                                                 None

            # Tries to retrieve "fe", "do" etc from molecules.dat
            symbols = ft.description_to_symbols(formula)
            if not symbols:
                a99.get_python_logger().warning("Formula '{}' not in internal BUILTIN_FORMULAS, "
                                                "and probably this molecule is also not in PFANT/data/common/molecules.dat".
                                                format(formula))

                symbols = ["", ""]
            else:
                m = bysym.get(tuple(symbols))
                if m:
                    fe = m.fe
                    do = m.do
                    am = m.am
                    bm = m.bm
                    ua = m.ua
                    ub = m.ub
                    te = m.te
                    cro = m.cro
                    s = m.s

            symbols = [x.strip() for x in symbols]
            conn.execute("insert into molecule "
                         "(formula, name, symbol_a, symbol_b, fe, do, am, bm, ua, ub, te, cro, s) "
                         "values (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         (
                         formula, name, symbols[0], symbols[1], fe, do, am, bm, ua, ub, te, cro, s))

            id_molecule = conn.execute("select last_insert_rowid() as id").fetchone()["id"]
            for state in data:
                # **Note** assumes that the columns in data match the
                # (number of columns in the state table - 2) and their order
                conn.execute("insert into state values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                             [None, id_molecule] + state)

            conn.commit()

        except:
            a99.get_python_logger().exception("Failed for molecule '{}'".format(formula))

    conn.close()
























def load_list_file(filename):
    """Loads a file containing (vl, v2l, FranckCondonFactor)

    ===begin exert===
    00 00 sj0000.dat .8638228E+00
    00 01 sj0001.dat .8712862E-01
    00 02 sj0002.dat .3144656E-01
    ===end exert===
    """


    fcfs = OrderedDict()
    with open(filename, "r") as h:
        for line in h:
            vl, v2l, _, fcf = line.strip().split(" ")
            vl = int(vl)
            v2l = int(v2l)
            fcf = float(fcf)
            fcfs[(vl, v2l)] = fcf
    return fcfs




# Correspondence between Franck-Condon Factors files and transitions
# Transition information taken from
# B.V. Castilho et al.: Beryllium abundance in lithium-rich giants, Astron. Astrophys. 345, 249–255 (1999)
#
# The .txt files were copied from Bruno's ATMOS:/wrk4/bruno/Mole/*. Their names were renamed to
# have the formula
FCF_MAP = (
("CH", "CH-sjalist.txt", "A", 2, 2, "X", 2, 1),  # A2Delta - X2Pi
("CH", "CH-sjblist.txt", "B", 2, 2, "X", 2, 1),  # B2Delta - X2Pi
("CH", "CH-sjclist.txt", "C", 2, 0, "X", 2, 1),  # C2Sigma - X2Pi
("NH", "NH-sjlist.txt", "A", 3, 1, "X", 3, 0),  # A3Pi - X3Sigma
("OH", "OH-sjlist.txt", "A", 2, 0, "X", 2, 1),  # A2Sigma - X2Pi
)


def insert_franck_condon_factors(moldb):
    conn = moldb.get_conn()
    assert isinstance(conn, sqlite3.Connection)

    for formula, filename, from_label, from_mult, from_spdf, to_label, to_mult, to_spdf in FCF_MAP:
        id_molecule = conn.execute("select id from molecule where formula = ?", (formula,))["id"]
        conn.execute("""insert into system (id_molecule, from_label, from_mult, from_spdf, to_label,
                        to_mult, to_spdf) values (?, ?, ?, ?, ?, ?, ?)""",
                     (id_molecule, from_label, from_mult, from_spdf, to_label, to_mult, to_spdf))

        fcf_dict = load_list_file(filename)
        for (vl, v2l), fcf in fcf_dict.items():
            conn.execute("insert into fcf")








if __name__ == "__main__":
    filename = ft.FileMolDB.default_filename

    if os.path.isfile(filename):
        if a99.yesno("File '{}' already exists, get rid of it and continue".format(filename), False):
            os.unlink(filename)
        else:
            sys.exit()

    f = ft.FileMolDB()
    f.filename = filename
    f.create_schema()
    # populate_moldb(f)
    insert_franck_condon_factors(f)

