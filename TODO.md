# TODO list



## GENERAL

- ~~**IMPORTANT** pip install not delivering the default data properly!!~~

- Enhance programs.py to sort alphabetically, generate single table (with word wrap). BTW it does not list itself
  Who cares which package. But I can filter in or out packages
 
- See why data files are not installing properly with pip setup.py install
  
- Documentation: **Get some inspiration** (read lots of shit)!!!!
- **Template project**
- Programs and file types listings: implement rst rendering
- & update explorer list_file_types() example


## Convmol

    - Conferir o DELTAK com a Beatriz!!!


    - moldbed.py:
    
        * equip with build-moldb.py
        

    - WMolecularConstants: system comes first, state to be searched automatically!   
    
    - FileMolDB: some tables still don't have the comment field??
    
    - Building database: fill in the state_label automatically, or maybe just search using the first letter
      (figure out if there is a "LIKE 'A%' as in MySQL) (no need to worry about speed here, we'll pre-compile the info for conversion)
      


# Filetypes

- new script to print filetypes as table
- actually it is better to specify max total width and wrap description accordingly

# Explorer

- Enhance explorer.py with options for spectra: save as... (have to figure out practical save as)
- mled.py: handle and test molecule and sol deletion

# x.py

- Throw new buttons in Abundances widget to expose export dissoc and export turbospectrum

## WSpectrumCollection

- Add spectrum when in Cube Editor: handle pixel-x and pixel-y properly
- Add export to SpectrumCollection: save as... (have to figure out practical save as)


## astrogear

  - Installation of other packages could write in f311 config file (or not)!!
  - **Sort the thing with DataFile.description**
  - implement categories in scripts (dunno, perhaps a `# cat: whatever`)

## pyfant

  - Fill origin when converting from FileFullCube to FileSpectrumList (somehow)
  - XHelpDialog is too ugly
  - Investigate what this a_XAtomsHistogram is about
  - Warn assumptions in ConvMol

  
## aosss

  - documentation: illustrate another case
  - perhaps scale-to-magnitude can be a a form of normalization


# Future suggestions

  - Find a way to obtain *any* Franck-Condon Factor needed
  - treat sqlite DB as config file (can wait)
  

# DONE

- ~~OPEN IN NEW WINDOW NOT COPYING EVERYTHIGN!!!!!~~
- NIST scraper: I can actually go after the "A" because it follows some pattern: points to footnote and there it is (this part is what I normally enjoy doing, so should enjoy)


- ~~FileSPectrumPfant not loading properly anymore!!~~
