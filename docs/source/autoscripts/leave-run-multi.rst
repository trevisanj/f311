.. code-block:: none

    usage: run-multi.py [-h] [--abs ABS] [--absoru ABSORU] [--aint AINT]
                        [--allow ALLOW] [--amores AMORES] [--convol CONVOL]
                        [--explain EXPLAIN] [--flam FLAM] [--flprefix FLPREFIX]
                        [--fn_abonds FN_ABONDS] [--fn_absoru2 FN_ABSORU2]
                        [--fn_atoms FN_ATOMS] [--fn_cv FN_CV]
                        [--fn_dissoc FN_DISSOC] [--fn_flux FN_FLUX]
                        [--fn_hmap FN_HMAP] [--fn_lines FN_LINES]
                        [--fn_log FN_LOG] [--fn_logging FN_LOGGING]
                        [--fn_main FN_MAIN] [--fn_modeles FN_MODELES]
                        [--fn_modgrid FN_MODGRID] [--fn_molecules FN_MOLECULES]
                        [--fn_moo FN_MOO] [--fn_opa FN_OPA]
                        [--fn_partit FN_PARTIT] [--fn_progress FN_PROGRESS]
                        [--fwhm FWHM] [--interp INTERP] [--kik KIK] [--kq KQ]
                        [--llfin LLFIN] [--llzero LLZERO]
                        [--logging_console LOGGING_CONSOLE]
                        [--logging_file LOGGING_FILE]
                        [--logging_level LOGGING_LEVEL] [--no_atoms NO_ATOMS]
                        [--no_h NO_H] [--no_molecules NO_MOLECULES] [--norm NORM]
                        [--opa OPA] [--pas PAS] [--pat PAT] [--play PLAY]
                        [--sca SCA] [--zinf ZINF] [--zph ZPH] [-f FN_ABXFWHM]
                        [-s CUSTOM_SESSION_ID]
    
    Runs pfant and nulbad in "multi mode" (equivalent to Tab 4 in ``x.py``) (several abundances X FWHM's)
    
    optional arguments:
      -h, --help            show this help message and exit
      --abs ABS
      --absoru ABSORU
      --aint AINT
      --allow ALLOW
      --amores AMORES
      --convol CONVOL
      --explain EXPLAIN
      --flam FLAM
      --flprefix FLPREFIX
      --fn_abonds FN_ABONDS
      --fn_absoru2 FN_ABSORU2
      --fn_atoms FN_ATOMS
      --fn_cv FN_CV
      --fn_dissoc FN_DISSOC
      --fn_flux FN_FLUX
      --fn_hmap FN_HMAP
      --fn_lines FN_LINES
      --fn_log FN_LOG
      --fn_logging FN_LOGGING
      --fn_main FN_MAIN
      --fn_modeles FN_MODELES
      --fn_modgrid FN_MODGRID
      --fn_molecules FN_MOLECULES
      --fn_moo FN_MOO
      --fn_opa FN_OPA
      --fn_partit FN_PARTIT
      --fn_progress FN_PROGRESS
      --fwhm FWHM
      --interp INTERP
      --kik KIK
      --kq KQ
      --llfin LLFIN
      --llzero LLZERO
      --logging_console LOGGING_CONSOLE
      --logging_file LOGGING_FILE
      --logging_level LOGGING_LEVEL
      --no_atoms NO_ATOMS
      --no_h NO_H
      --no_molecules NO_MOLECULES
      --norm NORM
      --opa OPA
      --pas PAS
      --pat PAT
      --play PLAY
      --sca SCA
      --zinf ZINF
      --zph ZPH
      -f FN_ABXFWHM, --fn_abxfwhm FN_ABXFWHM
                            Name of file specifying different abundances and
                            FWHM's (default: abxfwhm.py)
      -s CUSTOM_SESSION_ID, --custom_session_id CUSTOM_SESSION_ID
                            Name of directory where output files will be saved
                            (default: multi-session-<i>)
    

This script belongs to package *f311.pyfant*
