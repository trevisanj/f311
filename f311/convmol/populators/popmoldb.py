import a99
import f311.filetypes as ft
from ... import convmol as cm
from ... import pyfant as pf

__all__ = ["populate_moldb"]


def populate_moldb(moldb):
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
