# TODO list

## TODAY

Run all scripts

Review this mapping: try not to get rid of the plugin system but perhaps split it
  - file types
  - visualization types
  - scripts (programs.py)
  - default data: delegate to filetypes package



FileSPectrumPfant not loading properly anymore!!


## astrogear

  - ~~Make it work~~
  - ~~Figure out list of actions to plug things in~~
  - ~~Create a collaborator template~~
  - Installation of other packages could write in astroapi config file (or not)!!
  - Sort the thing with DataFile.description
  - ~~Look for PFANT~~
  - implement categories in scripts (dunno, perhaps a `# cat: whatever`)
  - allow for multiple database simultaneously somehow
  - treat sqlite DB as config file (can wait)

## pyfant

  - **SEE WHY PYFANT SETUP IS MESSING ASTROGEAR!!!!!!**

  - ~~OK implement ToScalar_UseNumPyFunc~~
  - ~~OK add combobox to XToScalar~~
  - ~~OK Smarter loading of Full Cube~~
  
  - ~~FIX MOLECULES FILE!!!!!
    comparing old x new moleculagrade
    perhaps best it is to keep both versions: contemplating diversity and whoever did whatever
    best would be to create an editor to mingle the molecules~~
  
  
  - Normalize("1") cause re-sampling, sth is not right
  - Fill origin when converting from FileFullCube to FileSpectrumList (somehow)
  - Get rid of WSpectrumList "More..." tab (make sure everything is implemented as blocks)
  - XHelpDialog is too ugly
  - Investigate what this a_XAtomsHistogram is about
  - Make sun Grevesse 1998 as default sun for pyfant
  - ~~legend=False in plot_*()~~
  - ~~p.conf.sid.clean() not intuitive~~
  - ~~easier to work with command line options~~
  - ~~nulbad load_result~~
  - Warn assumptions in ConvMol
  - ~~Resolve branches for other molecules~~ HITRAN OK

  
## aosss

  - documentation: illustrate another case
  - OK read and plot ESO sky tables
  - OK incorporate in the wavelength chart
  
