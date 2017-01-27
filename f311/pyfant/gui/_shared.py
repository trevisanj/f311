DESCR_MULTI = """
Runs pfant for different abundances for each element, then run nulbad for each
pfant result for different FWHMs.

The configuration is read from a .py file.

The user must specify a list of FWHM values for nulbad convolutions, and
a dictionary containing element symbols and respective list containing n_abdif
differential abundances to be used for each element.

pfant will be run n_abdif times, each time adding to each element in ab the i-th
value in the vector for the corresponding element.

nulbad will run n_abdif*n_fwhms times, where n_fwhms is the number of different
FWHMs specified.

The result will be
- several spectra saved as  "<star name><pfant name or counter>.sp"
- several "spectra list" files saved as "cv_<FWHM>.spl". As the file indicates,
  each ".spl" file will have the names of the spectrum files for a specific FWHM.
  .spl files are subject to input for lineplot.py by E.Cantelli
"""