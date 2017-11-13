.. code-block:: none

    usage: merge-molecules.py [-h] [-o [FN_OUTPUT]] files [files ...]
    
    Merges several PFANT molecular lines file into a single one
    
    positional arguments:
      files                 files specification: list of files, wildcards allowed
    
    optional arguments:
      -h, --help            show this help message and exit
      -o [FN_OUTPUT], --fn_output [FN_OUTPUT]
                            output filename. If not specified, creates file such
                            as 'molecules-merged-.0000.dat' (default: (automatic))
    

This script belongs to package *f311.pyfant*
