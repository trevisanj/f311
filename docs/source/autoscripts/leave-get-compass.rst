.. code-block:: none

    usage: get-compass.py [-h] [--max N] [--stage [STAGE]] N [N ...]
    
    Downloads WebSim-COMPASS simulations
    
    Based on shell script by Mathieu Puech
    
    **Note** Skips simulations for existing files in local directory starting with
             that simulation ID.
             Example: if it finds file(s) "C001006*", will skip simulation C001006
    
    **Note** Does not create any directory (actually creates it but deletes later).
             All files stored in local directory!
    
    **Note** Will work only on if os.name == "posix" (Linux, UNIX ...)
    
    positional arguments:
      N                List of simulation numbers (single value and ranges
                       accepted, e.g. 1004, 1004-1040)
    
    optional arguments:
      -h, --help       show this help message and exit
      --max N          Maximum number of simulations to get (default: 100)
      --stage [STAGE]  Websim-Compass pipeline stage: if specified, will download
                       files named, e.g., C000793_<stage>.fits (**note**: .par and
                       .out files are always downloaded) (default: all)
    

This script belongs to package *f311.aosss*
