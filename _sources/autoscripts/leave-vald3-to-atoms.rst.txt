.. code-block:: none

    usage: vald3-to-atoms.py [-h] [--min_algf [MIN_ALGF]] [--max_kiex [MAX_KIEX]]
                             fn_input [fn_output]
    
    Converts VALD3 atomic/molecular lines file to PFANT atomic lines file.
    
    Molecular lines are skipped.
    
    positional arguments:
      fn_input              input file name
      fn_output             output file name (default: atoms-untuned-<fn_input>)
    
    optional arguments:
      -h, --help            show this help message and exit
      --min_algf [MIN_ALGF]
                            minimum algf (log gf) (default: -7)
      --max_kiex [MAX_KIEX]
                            maximum kiex (default: 15)
    

This script belongs to package *f311.explorer*
