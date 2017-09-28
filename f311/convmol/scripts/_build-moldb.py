#!/usr/bin/env python
# coding: utf8
"""
Script to put together the file moldb.sqlite

**Note** This script is protected, but is very important to put to put together a lot of information
needed for molecular lines conversion (``convmol.py``)
"""

from f311 import filetypes as ft
import f311.convmol as cm
import a99
from collections import OrderedDict
import sqlite3
import os
import sys
from f311 import convmol as cm
from f311 import pyfant as pf

# FileMolecules
filemol = None
moldb = None


def my_info(s):
    a99.get_python_logger().info("[build-moldb] {}".format(s))


def insert_molecules():
    """Inserts data into the 'molecule' table"""

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

    conn.executemany("insert into molecule (formula, name) values (?,?)", MOLECULES)
    conn.commit()


def insert_systems():
    """Parses the systems out of the molecules descriptions in the PFANT molecular lines file"""


    # Collects PFANT systems
    # Iterates through the PFANT molecules to retrieve its systems.
    # Information is stored as MolConsts objects in which only the formula and system information are set
    rows = []
    for molecule in filemol:
        row = ft.MolConsts()
        row.populate_parse_str(molecule.description)

        print("FORMULA {}".format(row["formula"]))

        id_molecule = conn.execute("select id from molecule where formula = ?",
                                   (row["formula"],)).fetchone()["id"]

        # Inserts data into the 'system' table
        row_id = conn.execute("""select id from system where id_molecule = ? and from_label = ? and
           from_mult = ? and from_spdf = ? and to_label = ? and to_mult = ? and to_spdf = ?""",
                              (id_molecule, row["from_label"], row["from_mult"], row["from_spdf"],
                               row["to_label"], row["to_mult"], row["to_spdf"])).fetchone()
        if row_id is not None:
            id_system = row_id["id"]
        else:
            cursor = conn.execute("""insert into system (id_molecule, from_label, from_mult, from_spdf,
               to_label, to_mult, to_spdf, comments) values (?, ?, ?, ?, ?, ?, ?, ?)""",
                                  (id_molecule, row["from_label"], row["from_mult"], row["from_spdf"], row["to_label"],
            row["to_mult"], row["to_spdf"], ""))
            id_system = cursor.lastrowid

        # Inserts data into the 'pfantmol' table
        conn.execute("insert into pfantmol "
                     "(id_system, description, fe, do, am, bm, ua, ub, te, cro, s) "
                     "values (?,?,?,?,?,?,?,?,?,?,?)",
                     (id_molecule, molecule.description, molecule.fe, molecule.do, molecule.am,
                      molecule.bm, molecule.ua, molecule.ub, molecule.te,
                      molecule.cro, molecule.s))

    conn.commit()


def insert_pfantmol_data():
    """Inserts molecular header information 'PFANT/data/common/molecules.dat'"""

    # Uses PFANT/data/common/molecules.dat to retrieve "fe", "do", "am", etc.

    # bysym = dict([(tuple(m.symbols), m) for m in filemol])

    for molecule in filemol:
        id_molecule = conn.execute("select id from molecule where formula = ?",
                                   (ft.symbols_to_formula(molecule.symbols),)).fetchone()["id"]

        conn.execute("insert into pfantmol "
            "(id_molecule, description, fe, do, am, bm, ua, ub, te, cro, s) "
            "values (?,?,?,?,?,?,?,?,?,?,?)",
            (id_molecule, molecule.description, molecule.fe, molecule.do, molecule.am, molecule.bm, molecule.ua, molecule.ub, molecule.te,
            molecule.cro, molecule.s))
    conn.commit()


def insert_nist_data():
    """Tries to download data from NIST Web Book online"""

    for row in conn.execute("select id, formula from molecule order by id").fetchall():
        id_molecule, formula = row["id"], row["formula"]
        a99.get_python_logger().info("Molecule '{}'...".format(formula))
        try:
            data, _, _ = cm.get_nist_webbook_constants(formula)

            for state in data:
                # **Note** assumes that the columns in data match the
                # (number of columns in the state table - 2) and their order
                conn.execute("insert into state values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                             [None, id_molecule] + state + [""])

            conn.commit()

        except:
            a99.get_python_logger().exception("Failed for molecule '{}'".format(formula))
    conn.commit()


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








# Electronic systems
#
# # TODO calculate FCFs for Tio, FeH, C2, CO
SYSTEMS_MAP = (
("CH", "cha.out", "A", 2, 2, "X", 2, 1, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),  # A2Delta - X2Pi
("CH", "chb.out", "B", 2, 2, "X", 2, 1, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),
("CH", "chc.out", "C", 2, 0, "X", 2, 1, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),
("CN", "cnb.out", "B", 2, 0, "X", 2, 0, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),
("NH", "nha.out", "A", 3, 1, "X", 3, 0, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),  # A3Pi - X3Sigma
("OH", "oha.out", "A", 2, 0, "X", 2, 1, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),  # A2Sigma - X2Pi
("MgH", "mgha.out", "A", 2, 1, "X", 2, 0, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),
("MgH", "mghb.out", "B", 2, 0, "X", 2, 0, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),
)


def insert_systems_and_franck_condon_factors():

    for formula, filename, from_label, from_mult, from_spdf, to_label, to_mult, to_spdf, comments in SYSTEMS_MAP:
        id_molecule = conn.execute("select id from molecule where formula = ?",
                                   (formula,)).fetchone()["id"]
        cursor = conn.execute("""insert into system (id_molecule, from_label, from_mult, from_spdf,
           to_label, to_mult, to_spdf, comments) values (?, ?, ?, ?, ?, ?, ?, ?)""",
           (id_molecule, from_label, from_mult, from_spdf, to_label, to_mult, to_spdf, comments))
        id_system = cursor.lastrowid

        if filename is not None:
            # Can handle two different file formats
            try:
                a = ft.FileFCF()
                a.load(filename)
                fcf_dict = a.fcfs
            except:
                fcf_dict = load_list_file(filename)
            for (vl, v2l), fcf in fcf_dict.items():
                conn.execute("insert into fcf (id_system, vl, v2l, value) values (?,?,?,?)",
                             (id_system, vl, v2l, fcf))
    conn.commit()


if __name__ == "__main__":

    filename = ft.FileMolDB.default_filename

    if os.path.isfile(filename):
        if a99.yesno("File '{}' already exists, get rid of it and continue".format(filename), True):
            os.unlink(filename)
        else:
            sys.exit()

    yn = a99.yesno("Will now create file '{}'. Continue".format(filename), True)

    if not yn:
        sys.exit()

    filemol = ft.FileMolecules()
    filemol.load(pf.get_pfant_data_path("common", "molecules.dat"))

    moldb = ft.FileMolDB()
    moldb.filename = filename
    my_info("Creating schema...")
    moldb.create_schema()

    conn = moldb.get_conn()
    assert isinstance(conn, sqlite3.Connection)


    my_info("New filename: '{}'".format(moldb.filename))
    my_info("Inserting molecules...")
    insert_molecules()
    my_info("Inserting systems...")
    insert_systems()
    # my_info("Inserting Franck-Condon Factors from Bruno Castilho's work...")
    # insert_systems_and_franck_condon_factors(moldb)
    # my_info("Inserting molecule header information from '{}'...".
    #       format(pf.get_pfant_data_path("common", "molecules.dat")))
    # insert_pfantmol_data(moldb)
    # my_info("Inserting data from NIST Chemistry Web Book online...")
    # insert_nist_data(moldb)
