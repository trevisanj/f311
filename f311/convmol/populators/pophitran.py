# TODO outta here to new build-hitrandb.py
import a99
from .. import get_hitran_molecules, get_hitran_isotopologues
import f311.filetypes as ft

__all__ = ["populate_hitrandb"]


def populate_hitrandb(db):
    """Populates database with HITRAN data

    Populates a sqlite3 database represented by a FileHitranDB object with information downloaded
    from the HITRAN website

    Args:
        db: FileHitranDB instance
    """

    assert isinstance(db, ft.FileHitranDB)
    conn = db.get_conn()
    try:

        mols, _ = get_hitran_molecules()

        conn.executemany("insert into molecule values (?,?,?)", mols)

        a99.get_python_logger().info("Inserted {} molecules".format(len(mols)))

        for mol in mols:
            isos, _ = get_hitran_isotopologues(mol[0])

            for iso in isos:
                try:
                    conn.execute("insert into isotopologue values(?,?,?,?,?)",
                                 [iso[0], mol[0]] + iso[1:])
                except:
                    a99.get_python_logger().exception("Tried to insert this: {}".format(iso))
                    raise

            a99.get_python_logger().info("Inserted {} isotopologues for molecule '{}' ({})".
                                         format(len(isos), *mol[1:3]))
    finally:
        conn.commit()
        conn.close()

    conn.close()
