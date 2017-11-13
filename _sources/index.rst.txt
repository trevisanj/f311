F311 -- Astronomy-related Python 3 API and scripts
==================================================

Welcome

Introduction
------------

``f311`` is a Python 3 package containing many resources on selected topics in Astronomy.
Once installed, the package makes available a collection of scripts and an API
(application programming interface).

The package is organized in sub-packages, which can be imported as follows:

.. code::

    import f311.pyfant as pf
    import f311.convmol as cm
    import f311.explorer as ex
    import f311.filetypes as ft
    import f311.physics as ph
    import f311.aosss as ao


.. toctree::
   :maxdepth: 1

   install
   f3110
   pyfant
   convmol
   explorer
   filetypes
   physics
   aosss
   cheat

`Project F311 on GitHub <https://github.com/trevisanj/f311>`_

List of scripts
---------------







f311.aosss -- "Adaptive Optics Systems Simulation Support"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Graphical applications
^^^^^^^^^^^^^^^^^^^^^^

* :doc:`wavelength-chart.py <autoscripts/editable-wavelength-chart>`: Draws chart showing spectral lines of interest, spectrograph wavelength ranges, ESO atmospheric .

Command-line tools
^^^^^^^^^^^^^^^^^^

* :doc:`create-simulation-reports.py <autoscripts/editable-create-simulation-reports>`: Creates HTML reports from WebSim-COMPASS output files
* :doc:`create-spectrum-lists.py <autoscripts/editable-create-spectrum-lists>`: Create several .splist (spectrum list) files from WebSim-COMPASS output files; groups r
* :doc:`get-compass.py <autoscripts/editable-get-compass>`: Downloads WebSim-COMPASS simulations
* :doc:`list-mosaic-modes.py <autoscripts/editable-list-mosaic-modes>`: Lists MOSAIC Spectrograph modes
* :doc:`organize-directory.py <autoscripts/editable-organize-directory>`: Organizes simulation directory (creates folders, moves files, creates 'index.html')

f311.convmol -- Conversion of molecular lines files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Graphical applications
^^^^^^^^^^^^^^^^^^^^^^

* :doc:`convmol.py <autoscripts/editable-convmol>`: Conversion of molecular lines data to PFANT format
* :doc:`mced.py <autoscripts/editable-mced>`: Editor for molecular constants file
* :doc:`moldbed.py <autoscripts/editable-moldbed>`: Editor for molecules SQLite database

Command-line tools
^^^^^^^^^^^^^^^^^^

* :doc:`hitran-scraper.py <autoscripts/editable-hitran-scraper>`: Retrieves molecular lines from the HITRAN database [Gordon2016]
* :doc:`nist-scraper.py <autoscripts/editable-nist-scraper>`: Retrieves and prints a table of molecular constants from the NIST Chemistry Web Book.

f311.explorer -- Object-oriented framework to handle file types:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Graphical applications
^^^^^^^^^^^^^^^^^^^^^^

* :doc:`abed.py <autoscripts/editable-abed>`: Abundances file editor
* :doc:`ated.py <autoscripts/editable-ated>`: Atomic lines file editor
* :doc:`cubeed.py <autoscripts/editable-cubeed>`: Data Cube Editor, import/export WebSim-COMPASS data cubes
* :doc:`explorer.py <autoscripts/editable-explorer>`: F311 Explorer --  list, visualize, and edit data files (_à la_ File Manager)
* :doc:`mained.py <autoscripts/editable-mained>`: Main configuration file editor.
* :doc:`mled.py <autoscripts/editable-mled>`: Molecular lines file editor.
* :doc:`optionsed.py <autoscripts/editable-optionsed>`: PFANT command-line options file editor.
* :doc:`splisted.py <autoscripts/editable-splisted>`: Spectrum List Editor
* :doc:`tune-zinf.py <autoscripts/editable-tune-zinf>`: Tunes the "zinf" parameter for each atomic line in atomic lines file

Command-line tools
^^^^^^^^^^^^^^^^^^

* :doc:`create-grid.py <autoscripts/editable-create-grid>`: Merges several atmospheric models into a single file (_i.e._, the "grid")
* :doc:`cut-atoms.py <autoscripts/editable-cut-atoms>`: Cuts atomic lines file to wavelength interval specified
* :doc:`cut-molecules.py <autoscripts/editable-cut-molecules>`: Cuts molecular lines file to wavelength interval specified
* :doc:`cut-spectrum.py <autoscripts/editable-cut-spectrum>`: Cuts spectrum file to wavelength interval specified
* :doc:`plot-spectra.py <autoscripts/editable-plot-spectra>`: Plots spectra on screen or creates PDF file
* :doc:`vald3-to-atoms.py <autoscripts/editable-vald3-to-atoms>`: Converts VALD3 atomic/molecular lines file to PFANT atomic lines file.

f311.pyfant -- Python interface to the PFANT spectral synthesis software (Fortran)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Graphical applications
^^^^^^^^^^^^^^^^^^^^^^

* :doc:`x.py <autoscripts/editable-x>`: PFANT Launcher -- Graphical Interface for Spectral Synthesis

Command-line tools
^^^^^^^^^^^^^^^^^^

* :doc:`copy-star.py <autoscripts/editable-copy-star>`: Copies stellar data files (such as main.dat, abonds.dat, dissoc.dat) to local directory
* :doc:`link.py <autoscripts/editable-link>`: Creates symbolic links to PFANT data files as an alternative to copying these (sometimes large) files into local directoy
* :doc:`merge-molecules.py <autoscripts/editable-merge-molecules>`: Merges several PFANT molecular lines file into a single one
* :doc:`run-multi.py``: Runs pfant and nulbad in "multi mode" (equivalent to Tab 4 in ``x.py <autoscripts/editable-run-multi.py``: Runs pfant and nulbad in "multi mod)
* :doc:`run4.py <autoscripts/editable-run4>`: Runs the four Fortran binaries in sequence: `innewmarcs`, `hydro2`, `pfant`, `nulbad`





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

More
----

* :ref:`genindex` (all symbols listed alphabetically)
* :ref:`modindex` (whole f311 package tree)
* :ref:`search`
* :doc:`license`

.. image:: art/key-white.png
