# TODO list


## General

- **IMPORTANT** installing throguth pip not delivering the default data properly!!

- Enhance programs.py to sort alphabetically, generate single table (with word wrap). BTW it does not list itself
  Who cares which package. But I can filter in or out packages


## Convmol

  - Filter Kurucz


# Explorer

- Enhance explorer.py with options for spectra: save as... (have to figure out practical save as)
- mled.py: handle and test molecule and sol deletion

# x.py

- Throw new buttons in Abundances widget to expose export dissoc and export turbospectrum

## WSpectrumCollection

- ~~OPEN IN NEW WINDOW NOT COPYING EVERYTHIGN!!!!!~~
- Add spectrum when in Cube Editor: handle pixel-x and pixel-y properly
- Add export to SpectrumCollection: save as... (have to figure out practical save as)


## GENERAL

  
  - See why data files are not installing properly with pip setup.py install
  
- Documentation: **Get some inspiration** (read lots of shit)!!!!
- **Template project**
- ~~FileSPectrumPfant not loading properly anymore!!~~
- Programs and file types listings: implement rst rendering
- & update explorer list_file_types() example


## astrogear

  - Installation of other packages could write in f311 config file (or not)!!
  - **Sort the thing with DataFile.description**
  - implement categories in scripts (dunno, perhaps a `# cat: whatever`)
  - treat sqlite DB as config file (can wait)

## pyfant

  - Fill origin when converting from FileFullCube to FileSpectrumList (somehow)
  - XHelpDialog is too ugly
  - Investigate what this a_XAtomsHistogram is about
  - Warn assumptions in ConvMol

  
## aosss

  - documentation: illustrate another case

  

## Done
  - ~~Make sun Grevesse 1998 as default sun for pyfant~~
  - ~~nulbad load_result~~
  - ~~Get rid of WSpectrumList "More..." tab (make sure everything is implemented as blocks)~~
  - ~~**Normalize("1") cause re-sampling, sth is not right**~~
  - ~~Resolve branches for other molecules~~ HITRAN OK





# Future suggestions

  - Find a way to obtain *any* Franck-Condon Factor needed
  