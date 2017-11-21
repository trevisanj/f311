# TODO list

## GENERAL

- simplify directory structure. Expose all the shit

- Introduce "notes" field for main.dat: could be sth like "<star name> # <notes>"

- x.py, tab 3: verify if files exist

- File .spec taking too long to open

- x.py, tab 3: raiing exception if edit field is empty

- explorer.py: opening extra window

- run4.py + fileoptions + x.py tab3: move documentation ifnroamtion to inside fileoptions so that I can publish the descriptions of the parameters in `run4.py --help`

- Custom session directory: when types, select the ckechbox automatically

- abed: Element Abundance (A(X)(ref)) (A(X)) [X/Fe]; A(X) is the current informationz    

- Enhance programs.py to sort alphabetically, generate single table (with word wrap). BTW it does not list itself
  Who cares which package. But I can filter in or out packages
  
- new script to print filetypes as table

- programs.py: verbose collection of programs; show paths

- Enhance explorer.py with options for spectra: save as... (have to figure out practical save as)

- mled.py: handle and test molecule and sol deletion

- Throw new buttons in Abundances widget to expose export dissoc and export turbospectrum

- WSpectrumCollection: Add spectrum when in Cube Editor: handle pixel-x and pixel-y properly

- WSpectrumCollection: Add export to SpectrumCollection: save as... (have to figure out practical save as)

- Fill origin when converting from FileFullCube to FileSpectrumList (somehow)

- XHelpDialog is too ugly

## Documentation

- remove "editable-" from script pages because it makes ugly urls

- write down lots of examples

- Release notes: roughly what has been done since the beginning

- & update explorer list_file_types() example

- Programs and file types listings: implement rst rendering option (?)

### Specific examples

- pyfant: varying "pas"

- scripts: one page per script

- aosss: perhaps a fullcube tutorial


# Future suggestions

- Find a way to obtain *any* Franck-Condon Factor needed

- implement categories in scripts (perhaps a `# cat: whatever` in the source code)

