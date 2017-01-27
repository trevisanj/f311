#!/usr/bin/env python3


from pyfant.convmol import moldb

if __name__ == "__main__":
    moldb.create_db()
    moldb.populate_db()