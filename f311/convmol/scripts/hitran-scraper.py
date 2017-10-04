#!/usr/bin/env python

"""
Retrieves molecular lines from the HITRAN database [Gordon2016]

This script uses web scraping and the HAPI to save locally molecular lines from the HITRAN database.

While the HAPI provides the downloading facility, web scraping is used to get the lists of molecules
and isotopologues from the HITRAN webpages and get the IDs required to run the HAPI query.

The script is typically invoked several times, each time with an additional argument.

References:

[Gordon2016] I.E. Gordon, L.S. Rothman, C. Hill, R.V. Kochanov, Y. Tan, P.F. Bernath, M. Birk,
    V. Boudon, A. Campargue, K.V. Chance, B.J. Drouin, J.-M. Flaud, R.R. Gamache, J.T. Hodges,
    D. Jacquemart, V.I. Perevalov, A. Perrin, K.P. Shine, M.-A.H. Smith, J. Tennyson, G.C. Toon,
    H. Tran, V.G. Tyuterev, A. Barbe, A.G. Császár, V.M. Devi, T. Furtenbacher, J.J. Harrison,
    J.-M. Hartmann, A. Jolly, T.J. Johnson, T. Karman, I. Kleiner, A.A. Kyuberis, J. Loos,
    O.M. Lyulin, S.T. Massie, S.N. Mikhailenko, N. Moazzen-Ahmadi, H.S.P. Müller, O.V. Naumenko,
    A.V. Nikitin, O.L. Polyansky, M. Rey, M. Rotger, S.W. Sharpe, K. Sung, E. Starikova,
    S.A. Tashkun, J. Vander Auwera, G. Wagner, J. Wilzewski, P. Wcisło, S. Yu, E.J. Zak,
    The HITRAN2016 Molecular Spectroscopic Database, J. Quant. Spectrosc. Radiat. Transf. (2017).
    doi:10.1016/j.jqsrt.2017.06.038.
"""

import argparse
import logging
import a99
import tabulate
import sys
import os
from f311 import hapi
import f311.filetypes as ft
import f311.physics as ph

_DEF_T = '(molecular formula)'
_DEF_M = '(lists molecules)'
_DEF_I = '(lists isotopologues)'
_DEF_LL = None


if __name__ == "__main__":
    a99.logging_level = logging.INFO
    a99.flag_log_file = True
    script_name = os.path.basename(__file__)

    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('-t', type=str, help='Table Name',
                        default=_DEF_T, nargs=1)
    parser.add_argument('M', type=str, help='HITRAN molecule number',
                        default=_DEF_M, nargs='?')
    parser.add_argument('I', type=str,
                        help='HITRAN isotopologue number (not unique, starts over at each molecule)',
                        default=_DEF_I, nargs='?')
    parser.add_argument('llzero', type=float,
                        help='Initial wavelength (Angstrom)',
                        default=_DEF_LL, nargs='?')
    parser.add_argument('llfin', type=float,
                        help='Final wavelength (Angstrom)',
                        default=_DEF_LL, nargs='?')
    # parser.add_argument('llzero', type=str,
    # help='initial wavelength (',
    # default='()', nargs='?')
    # parser.add_argument('I', type=str,
    # help='HITRAN isotopologue number (not unique, starts over at each molecule',
    # default='()', nargs='?')
    args = parser.parse_args()

    db = ft.FileHitranDB()
    db.init_default()
    if args.M == _DEF_M:
        print()
        print("\n".join(a99.format_h1("List of all HITRAN molecules")))
        print()
        # Lists all molecules from local cache of HITRAN molecules
        print(tabulate.tabulate(*a99.cursor_to_data_header(db.query_molecule())))
        print()
        print("Now, to list isotopologues for a given molecule, please type:")
        print()
        print("    {} <molecule ID>".format(script_name))
        print()
        print("where <molecule ID> is one of the IDs listed above.")
    elif args.I == _DEF_I:
        row0 = db.query_molecule(ID=args.M).fetchone()
        if row0 is None:
            a99.print_error("Molecule ID {} not found".format(args.M))
            sys.exit()

        print()
        print("\n".join(a99.format_h1("List of all isotopologues for molecule '{Formula}' ({Name})".
                                     format(**row0))))
        print()
        # Lists all molecules from local cache of HITRAN molecules
        print(tabulate.tabulate(*a99.cursor_to_data_header(
            db.query_isotopologue(**{"molecule.ID": args.M}))))
        print()
        print("Now, to download lines, please type:")
        print()
        print("    {} {} <isotopologue ID> <llzero> <llfin>".format(script_name, args.M))
        print()
        print("where <isotopologue ID> is one the numbers from the 'ID' column above,")
        print()
        print("and [<llzero>, <llfin>] defines the wavelength interval in Angstrom.")
        print()
    else:
        row0 = db.query_molecule(ID=args.M).fetchone()
        if row0 is None:
            a99.print_error("Molecule ID {} not found".format(args.M))
        else:
            kwargs = {"molecule.id": args.M, "isotopologue.ID": args.I}
            row1 = db.query_isotopologue(**kwargs).fetchone()
            if row1 is None:
                a99.print_error("Isotopologue ({}, {}) not found".format(args.M, args.I))
                sys.exit()

            print()
            print("\n".join(a99.format_h1("Isotopologue selected:")))
            print()
            print(tabulate.tabulate(list(row1.items()), ["Field name", "Value"]))
            print()

            if args.llzero == _DEF_LL or args.llfin == _DEF_LL:
                print("To download lines for this isotopologue, please type:")
                print()
                print("    {} {} {} <llzero> <llfin>".format(script_name, args.M, args.I))
                print()
                print("where [<llzero>, <llfin>] makes the wavelength interval in Angstrom.")
                print()
                sys.exit()

            print("Wavelength interval (air): [{llzero}, {llfin}] Angstrom".format(**args.__dict__))
            if args.llzero >= args.llfin:
                a99.print_error("Initial wavelength must be lower than Final wavelength")
                sys.exit()

            # Here will fetch data
            wn0 = ph.air_to_vacuum(1e8/args.llzero)
            wn1 = ph.air_to_vacuum(1e8/args.llfin)
            print("Wavenumber interval (vacuum): [{}, {}] cm**-1".format(wn1, wn0))

            table_name = args.t if args.t != _DEF_T else row1["Formula"]
            print("Table name: '{}'".format(table_name))
            print()
            print("Fetching data...")
            print("===")
            print("=== BEGIN messages from HITRAN API ===")
            print("===")
            hapi.fetch(table_name, int(args.M), int(args.I), wn1, wn0)

            print("===")
            print("=== END messages from HITRAN API ===")
            print("===")
            print("...done")
            print("Please check files '{0}.header', '{0}.data'".format(table_name))





    # kwargs = {}
    # if not args.ID == "(all)":
    #     kwargs["molecule.ID"] = args.ID
    #
    # pf.hitrandb.print_isotopologues(**kwargs)