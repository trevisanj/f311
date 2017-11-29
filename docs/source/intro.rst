Introduction
============

``f311`` is a Python 3 package containing many resources on selected topics in Astronomy.
Once installed, the package makes available a collection of scripts and an API
(application programming interface).

Using the API
-------------

The API is organized in sub-packages, which can be imported as follows:

.. code::

    import f311.pyfant as pf
    import f311.convmol as cm
    import f311.explorer as ex
    import f311.filetypes as ft
    import f311.physics as ph
    import f311.aosss as ao

For convenience, the symbols of the subpackages are exposed at the root package level, so
another way to import the API is:

.. code::

    import f311

Contributing to this project
----------------------------

If you would like to contribute to this project, you can clone the source code on
`GitHub <https://github.com/trevisanj/f311>`_.

List of scripts
---------------

f311.aosss -- "Adaptive Optics Systems Simulation Support"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Graphical applications
^^^^^^^^^^^^^^^^^^^^^^

* :doc:`wavelength-chart.py <autoscripts/script-wavelength-chart>`: Draws chart showing spectral lines of interest, spectrograph wavelength ranges, ESO atmospheric .

Command-line tools
^^^^^^^^^^^^^^^^^^

* :doc:`create-simulation-reports.py <autoscripts/script-create-simulation-reports>`: Creates HTML reports from WebSim-COMPASS output files
* :doc:`create-spectrum-lists.py <autoscripts/script-create-spectrum-lists>`: Create several .splist (spectrum list) files from WebSim-COMPASS output files; groups r
* :doc:`get-compass.py <autoscripts/script-get-compass>`: Downloads WebSim-COMPASS simulations
* :doc:`list-mosaic-modes.py <autoscripts/script-list-mosaic-modes>`: Lists MOSAIC Spectrograph modes
* :doc:`organize-directory.py <autoscripts/script-organize-directory>`: Organizes simulation directory (creates folders, moves files, creates 'index.html')

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





.. hint::

   You can use ``programs.py`` to list available scripts.


List of acronyms
----------------

**API** -- application programming interface

**GUI** -- graphical user interface

**FWHM** -- full with at half maximum



Acknowledgement
---------------

The project started in 2015 at IAG-USP (Institute of Astronomy, Geophysics and Atmospheric Sciences
at University of São Paulo, Brazil).

Partially funded by FAPESP - Research Support Foundation of the State of São Paulo, Brazil (2015-2017).
