Index of applications (scripts)
===============================

.. only:: html

    f311.convmol -- Conversion of molecular lines files.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Graphical applications
    ^^^^^^^^^^^^^^^^^^^^^^

    * :doc:`convmol.py <autoscripts/script-convmol>`: Conversion of molecular lines data to PFANT format
    * :doc:`mced.py <autoscripts/script-mced>`: Editor for molecular constants file
    * :doc:`moldbed.py <autoscripts/script-moldbed>`: Editor for molecules SQLite database

    Command-line tools
    ^^^^^^^^^^^^^^^^^^

    * :doc:`hitran-scraper.py <autoscripts/script-hitran-scraper>`: Retrieves molecular lines from the HITRAN database [Gordon2016]
    * :doc:`nist-scraper.py <autoscripts/script-nist-scraper>`: Retrieves and prints a table of molecular constants from the NIST Chemistry Web Book.

    f311.explorer -- Object-oriented framework to handle file types:
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Graphical applications
    ^^^^^^^^^^^^^^^^^^^^^^

    * :doc:`abed.py <autoscripts/script-abed>`: Abundances file editor
    * :doc:`ated.py <autoscripts/script-ated>`: Atomic lines file editor
    * :doc:`cubeed.py <autoscripts/script-cubeed>`: Data Cube Editor, import/export WebSim-COMPASS data cubes
    * :doc:`explorer.py <autoscripts/script-explorer>`: F311 Explorer --  list, visualize, and edit data files (_à la_ File Manager)
    * :doc:`mained.py <autoscripts/script-mained>`: Main configuration file editor.
    * :doc:`mled.py <autoscripts/script-mled>`: Molecular lines file editor.
    * :doc:`optionsed.py <autoscripts/script-optionsed>`: PFANT command-line options file editor.
    * :doc:`splisted.py <autoscripts/script-splisted>`: Spectrum List Editor
    * :doc:`tune-zinf.py <autoscripts/script-tune-zinf>`: Tunes the "zinf" parameter for each atomic line in atomic lines file

    Command-line tools
    ^^^^^^^^^^^^^^^^^^

    * :doc:`create-grid.py <autoscripts/script-create-grid>`: Merges several atmospheric models into a single file (_i.e._, the "grid")
    * :doc:`cut-atoms.py <autoscripts/script-cut-atoms>`: Cuts atomic lines file to wavelength interval specified
    * :doc:`cut-molecules.py <autoscripts/script-cut-molecules>`: Cuts molecular lines file to wavelength interval specified
    * :doc:`cut-spectrum.py <autoscripts/script-cut-spectrum>`: Cuts spectrum file to wavelength interval specified
    * :doc:`plot-spectra.py <autoscripts/script-plot-spectra>`: Plots spectra on screen or creates PDF file
    * :doc:`vald3-to-atoms.py <autoscripts/script-vald3-to-atoms>`: Converts VALD3 atomic/molecular lines file to PFANT atomic lines file.

    f311.pyfant -- Python interface to the PFANT spectral synthesis software (Fortran)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Graphical applications
    ^^^^^^^^^^^^^^^^^^^^^^

    * :doc:`x.py <autoscripts/script-x>`: PFANT Launcher -- Graphical Interface for Spectral Synthesis

    Command-line tools
    ^^^^^^^^^^^^^^^^^^

    * :doc:`copy-star.py <autoscripts/script-copy-star>`: Copies stellar data files (such as main.dat, abonds.dat, dissoc.dat) to local directory
    * :doc:`link.py <autoscripts/script-link>`: Creates symbolic links to PFANT data files as an alternative to copying these (sometimes large) files into local directoy
    * :doc:`merge-molecules.py <autoscripts/script-merge-molecules>`: Merges several PFANT molecular lines file into a single one
    * :doc:`run-multi.py``: Runs pfant and nulbad in "multi mode" (equivalent to Tab 4 in ``x.py <autoscripts/script-run-multi.py``: Runs pfant and nulbad in "multi mod)
    * :doc:`run4.py <autoscripts/script-run4>`: Runs the four Fortran binaries in sequence: `innewmarcs`, `hydro2`, `pfant`, `nulbad`


.. only:: latex

    This chapter is a reference to all scripts in project F311.


    .. toctree::
        :maxdepth: 1

        autoscripts/script-create-simulation-reports
        autoscripts/script-create-spectrum-lists
        autoscripts/script-get-compass
        autoscripts/script-list-mosaic-modes
        autoscripts/script-organize-directory
        autoscripts/script-wavelength-chart
        autoscripts/script-hitran-scraper
        autoscripts/script-nist-scraper
        autoscripts/script-convmol
        autoscripts/script-mced
        autoscripts/script-moldbed
        autoscripts/script-create-grid
        autoscripts/script-cut-atoms
        autoscripts/script-cut-molecules
        autoscripts/script-cut-spectrum
        autoscripts/script-plot-spectra
        autoscripts/script-vald3-to-atoms
        autoscripts/script-abed
        autoscripts/script-ated
        autoscripts/script-cubeed
        autoscripts/script-explorer
        autoscripts/script-mained
        autoscripts/script-mled
        autoscripts/script-optionsed
        autoscripts/script-splisted
        autoscripts/script-tune-zinf
        autoscripts/script-copy-star
        autoscripts/script-link
        autoscripts/script-merge-molecules
        autoscripts/script-run-multi
        autoscripts/script-run4
        autoscripts/script-x