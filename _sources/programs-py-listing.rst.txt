``programs.py`` listing
=======================

.. code:: shell

    programs.py

::

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
