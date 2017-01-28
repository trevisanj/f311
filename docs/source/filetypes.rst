*f311.filetypes*: file handling API
===================================

Introduction
------------

*f311.filetypes* has classes to handle many different file formats used in Astronomy.

All classes descend from :any:`DataFile` containing some basic methods:

- ``load()``: loads file from disk into internal object variables
- ``save_as()``: saves file to disk
- ``init_default()``: initializes file object with default information

Examples
--------

The following example generates a random spectrum and saves it to disk as a FITS file.

.. code:: python


    import f311.filetypes as ft
    import numpy as np
    f = ft.FileSpectrumFits()
    f.spectrum.wavelength = np.linspace(5000., 5100., 100.)  # angstrom
    f.spectrum.flux = np.random.random(100)+2.
    f.save_as("random-spectrum.fits")


The following code lists all supported data types in a table:

.. code:: python

    import f311.filetypes as ft
    print("\n".join(ft.list_data_types()))

::

    File type                                                     | Default filename (for all purposes)
    ------------------------------------------------------------- | -----------------------------------
    "Absoru2" file                                                | absoru2.dat
    "Lambda-flux" Spectrum (2-column text file)                   | -
    Atmospheric model or grid of models (with opacities included) | grid.moo
    Configuration file saved as a .py Python source script        | -
    FITS Data Cube ("full" opposed to "sparse")                   | default.fullcube
    FITS Sparse Data Cube (storage to take less disk space)       | default.sparsecube
    FITS Spectrum                                                 | -
    FITS Spectrum List                                            | default.splist
    FileHitranDB                                                  | hitrandb.sqlite
    FileMolDB                                                     | moldb.sqlite
    FileSQLiteDB                                                  | -
    FileSpectrum                                                  | -
    Generic representation of a FITS file                         | -
    Kurucz molecular lines file                                   | -
    MARCS ".opa" (opacity model) file format.                     | modeles.opa
    MARCS Atmospheric Model (text file)                           | -
    PFANT Atmospheric Model (binary file)                         | modeles.mod
    PFANT Atomic Lines                                            | atoms.dat
    PFANT Hydrogen Line Profile                                   | thalpha
    PFANT Hygrogen Lines Map                                      | hmap.dat
    PFANT Molecular Lines                                         | molecules.dat
    PFANT Partition Function                                      | partit.dat
    PFANT Spectrum (`nulbad` output)                              | -
    PFANT Spectrum (`pfant` output)                               | flux.norm
    PFANT Stellar Chemical Abundances                             | abonds.dat
    PFANT Stellar Dissociation Equilibrium Information            | dissoc.dat
    PFANT Stellar Main Configuration                              | main.dat
    VALD3 atomic or molecular lines file                          | -
    WebSim-COMPASS ".par" (parameters) file                       | -
    `x.py` Command-line Options                                   | options.py
    `x.py` Differential Abundances and FWHMs (Python source)      | abxfwhm.py

API reference
-------------

:doc:`autodoc/f311.filetypes`
