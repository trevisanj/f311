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

.. code:: shell

Running ``programs.py`` on the shell will print something like this::

    Package 'aosss'
    ===============

      Graphical applications
      ----------------------

        wavelength-chart.py ......... Draws chart showing spectral lines of
                                      interest, spectrograph wavelength ranges, ESO
                                      atmospheric model, etc.

      Command-line tools
      ------------------

        create-simulation-reports.py  Creates HTML reports from WebSim-COMPASS
                                      output files
        create-spectrum-lists.py .... Create several .splist (spectrum list) files
                                      from WebSim-COMPASS output files; groups
                                      spectra that share same wavelength vector
        get-compass.py .............. Downloads WebSim-COMPASS simulations
        list-mosaic-modes.py ........ Lists MOSAIC Spectrograph modes
        organize-directory.py ....... Organizes simulation directory (creates
                                      folders, moves files, creates 'index.html')

    Package 'convmol'
    =================

      Graphical applications
      ----------------------

        convmol.py ........ Conversion of molecular lines data to PFANT format

      Command-line tools
      ------------------

        download-hitran.py  Downloads molecular lines from HITRAN database
        print-nist.py ..... Downloads and prints molecular constants from NIST Web
                            Book for a particular molecule

    Package 'explorer'
    ==================

      Graphical applications
      ----------------------

        abed.py .......... Abundances file editor
        ated.py .......... Atomic lines file editor
        cubeed.py ........ Data Cube Editor, import/export WebSim-COMPASS data cubes
        explorer.py ...... F311 Explorer --  list, visualize, and edit data files
                           (_à la_ File Manager)
        mained.py ........ Main configuration file editor.
        mled.py .......... Molecular lines file editor.
        splisted.py ...... Spectrum List Editor
        tune-zinf.py ..... Tunes the "zinf" parameter for each atomic line in atomic
                           lines file

      Command-line tools
      ------------------

        create-grid.py ... Merges several atmospheric models into a single file
                           (_i.e._, the "grid")
        cut-atoms.py ..... Cuts atomic lines file to wavelength interval specified
        cut-molecules.py . Cuts molecular lines file to wavelength interval
                           specified
        cut-spectrum.py .. Cuts spectrum file to wavelength interval specified
        plot-spectra.py .. Plots spectra on screen or creates PDF file
        vald3-to-atoms.py  Converts VALD3 atomic/molecular lines file to PFANT
                           atomic lines file.

    Package 'pyfant'
    ================

      Graphical applications
      ----------------------

        x.py ........ PFANT Launcher -- Graphical Interface for Spectral Synthesis

      Command-line tools
      ------------------

        copy-star.py  Copies stellar data files (such as main.dat, abonds.dat,
                      dissoc.dat) to local directory
        link.py ..... Creates symbolic links to PFANT data files as an alternative
                      to copying these (sometimes large) files into local directory
        run4.py ..... Runs the four Fortran binaries in sequence: `innewmarcs`,
                      `hydro2`, `pfant`, `nulbad`
        save-pdf.py . Looks for files "*.norm" inside directories session-* and
                      saves one figure per page in a PDF file

    PFANT Fortran binaries
    ======================

        innewmarcs  found
        hydro2 .... found
        pfant ..... found
        nulbad .... found




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
