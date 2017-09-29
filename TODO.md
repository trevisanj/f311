# TODO list

## Ask BLB

- Conferir o DELTAK com a Beatriz!!!


## GENERAL

- File .spec taking too long to open

- Custom session directory: when types, select the ckechbox automatically

- abed: Element Abundance (A(X)(ref)) (A(X)) [X/Fe]; A(X) is the current informationz    

- Introduce "notes" field for main.dat


- Enhance programs.py to sort alphabetically, generate single table (with word wrap). BTW it does not list itself
  Who cares which package. But I can filter in or out packages
 
  
- **Template project**
- Programs and file types listings: implement rst rendering
- & update explorer list_file_types() example


### Documentation

- Release notes: roughly what has been done since the beginning

- Examples/demos: I think that a good way is to write tests first, each "def test_*()" who wishes to become a demo will have to have a nice docstring,
and I am pretty sure I can write a script to replace the "def test_<sthsth>(...)" with a "if __name__ == '__main__'" ... and so on; and I guess that I can make these appear in sphinx doc too... 
further investigation required


- Write something useful instead of this. Put screenshots at front, better

    ``explorer.py`` (:doc:`screenshot <explorer-py-screenshot>`) is perhaps the application of broadest interest.
    It is a file browser that allows you to visualize and edit many file formats used in Astronomy. Its file-handling abilities can be
    easily expanded.


- I think it is better to write tests, then see some of them becoming examples. Yeah there is no way to avoid all redundance.
  But strategies can be drawn.

- Bring more examples and find a way to organize them both in the code and in the documentation


## Convmol

- moldbed.py:

    * equip with build-moldb.py
    



- Building database: fill in the state_label automatically, or maybe just search using the first letter
  (figure out if there is a "LIKE 'A%' as in MySQL) (no need to worry about speed here, we'll pre-compile the info for conversion)    


# Filetypes

- new script to print filetypes as table
- actually it is better to specify max total width and wrap description accordingly

# Explorer

- programs.py: verbose collection of programs; show paths
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

- ~~NIST scraper: I can actually go after the "A" because it follows some pattern: points to footnote and there it is (this part is what I normally enjoy doing, so should enjoy)~~

- ~~FileSPectrumPfant not loading properly anymore!!~~

- ~~**IMPORTANT** pip install not delivering the default data properly!!~~

- ~~See why data files are not installing properly with pip setup.py install~~

- ~~FileMolDB: some tables still don't have the comment field??~~

- ~~NIST scrapper no longer working for all molecules~~

- ~~Introduce "notes" field for abonds.dat~~

- ~~Review doublet: This may be wrong, this thing with LBIG or SMALL, gotta check again~~

- ~~WMolecularConstants: system comes first, state to be searched automatically!~~   
