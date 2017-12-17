.. code-block:: none

    usage: plot-spectra.py [-h] [--ovl | --pieces | --pages] [--aint [AINT]]
                           [--fn_output [FN_OUTPUT]] [--ymin [YMIN]]
                           [-r [NUM_ROWS]]
                           fn [fn ...]
    
    Plots spectra on screen or creates PDF file
    
    It can work in four different modes:
    
    a) grid of sub-plots, one for each spectrum (default mode)
       Example:
       plot-spectra.py flux.norm.nulbad measured.fits
    
    b) single plot with all spectra overlapped ("--ovl" option)
       Example:
       > plot-spectra.py --ovl flux.norm.nulbad measured.fits
    
    c) PDF file with a small wavelength interval per page ("--pieces" option).
       This is useful to flick through a large wavelength range.
       Example:
       > plot-spectra.py --pieces --aint 7 flux.norm.nulbad measured.fits
    
    d) PDF file with one spectrum per page ("--pages" option).
       Example:
       > plot-spectra.py --pages flux.*
    
    Types of files supported:
    
      - pfant output, e.g., flux.norm;
      - nulbad output, e.g., flux.norm.nulbad;
      - 2-column "lambda-flux" generic text files;
      - FITS files.
    
    positional arguments:
      fn                    name of spectrum file(s) (many types supported)
                            (wildcards allowed, e.g., "flux.*")
    
    optional arguments:
      -h, --help            show this help message and exit
      --ovl                 Overlapped graphics (default: False)
      --pieces              If set, will generate a PDF file with each page
                            containing one "piece" of the spectra of lengthgiven
                            by the --aint option. (default: False)
      --pages               If set, will generate a PDF file with one spectrum per
                            page (default: False)
      --aint [AINT]         length of each piece-plot in wavelength units (used
                            only if --pieces) (default: 10)
      --fn_output [FN_OUTPUT]
                            PDF output file name (used only if --pieces) (default:
                            (plot-spectra-<xxxx>.pdf))
      --ymin [YMIN]         Minimum value for y-axis (default: (automatic))
      -r [NUM_ROWS], --num_rows [NUM_ROWS]
                            Number of rows in subplot grid (default: (automatic))
    

This script belongs to package *f311*
