.. code-block:: none

    usage: create-spectrum-lists.py [-h] [--stage [STAGE]]
    
    Create several .splist (spectrum list) files from WebSim-COMPASS output files; groups spectra that share same wavelength vector
    
    All spectra in each .splist file will have the same wavelength vector
    
    optional arguments:
      -h, --help       show this help message and exit
      --stage [STAGE]  Websim-Compass pipeline stage (will collect files named,
                       e.g., C000793_<stage>.fits) (default: spintg)
    

This script belongs to package *f311.aosss*
