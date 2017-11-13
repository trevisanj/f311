.. code-block:: none

    usage: create-grid.py [-h] [--pattern [PATTERN]]
                          [--mode [{opa,modtxt,modbin}]]
                          [fn_output]
    
    Merges several atmospheric models into a single file (_i.e._, the "grid")
    
    "Collects" several files in current directory and creates a single file
    containing atmospheric model grid.
    
    Working modes (option "-m"):
     "opa" (default mode): looks for MARCS[1] ".mod" and ".opa" text file pairs and
                           creates a *big* binary file containing *all* model
                           information including opacities.
                           Output will be in ".moo" format.
    
     "modtxt": looks for MARCS ".mod" text files only. Resulting grid will not contain
               opacity information.
               Output will be in binary ".mod" format.
    
     "modbin": looks for binary-format ".mod" files. Resulting grid will not contain
               opacity information.
               Output will be in binary ".mod" format.
    
    References:
      [1] http://marcs.astro.uu.se/
    
    .
    .
    .
    
    positional arguments:
      fn_output             output file name (default: "grid.moo" or "grid.mod",
                            depending on mode)
    
    optional arguments:
      -h, --help            show this help message and exit
      --pattern [PATTERN]   file name pattern (with wildcards) (default: *.mod)
      --mode [{opa,modtxt,modbin}]
                            working mode (see description above) (default: opa)
    

This script belongs to package *f311.explorer*
