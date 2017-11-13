.. code-block:: none

    usage: tune-zinf.py [-h] [--min [MIN]] [--max [MAX]] [--inflate [INFLATE]]
                        [--ge_current] [--no_clean]
                        fn_input [fn_output]
    
    Tunes the "zinf" parameter for each atomic line in atomic lines file
    
    The "zinf" parameter is a distance in angstrom from the centre of an atomic
    line. It specifies the calculation range for the line:
    [centre-zinf, centre+zinf].
    
    This script runs pfant for each atomic line to determine the width of each
    atomic line and thus zinf.
    
    Note: pfant is run using most of its default settings and will require the
    following files to exist in the current directory:
      - main.dat
      - dissoc.dat
      - abonds.dat
      - modeles.mod
      - partit.dat
      - absoru2.dat
    
    Note: the precision in the zinf found depends on the calculation step ("pas")
    specified in main.dat. A higher "pas" means lower precision and a tendency to
    get higher zinf's. This is really not critical. pas=0.02 or pas=0.04 should do.
    
    positional arguments:
      fn_input             input file name
      fn_output            output file name (default: <made-up filename>)
    
    optional arguments:
      -h, --help           show this help message and exit
      --min [MIN]          minimum zinf. If zinf found for a particular line is
                           smaller than this value, this value will be used
                           instead (default: 0.1)
      --max [MAX]          maximum zinf. If zinf found for a particular line is
                           greater than this value, this value will be used
                           instead (default: 50.0)
      --inflate [INFLATE]  Multiplicative constant to apply a "safety margin".
                           Each zinf found will be multiplied by this value. For
                           example a value of INFLATE=1.1 means that all the
                           zinf's saved will be 10 percent larger than those
                           calculated (default: 1.1)
      --ge_current         "Greater or Equal to current": If this option is set,
                           the current zinf in the atomic lines file is used as a
                           lower boundary. (default: False)
      --no_clean           If set, will not remove the session directories.
                           (default: False)
    

This script belongs to package *f311.explorer*
