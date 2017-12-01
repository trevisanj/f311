File handling API
=================

Introduction
------------

*f311.filetypes* represents most of the non-visual essence of the F311 project.
the. That package has classes to handle many different file formats used in Astronomy.

All classes descend from :any:`DataFile` containing some basic methods:

- ``load()``: loads file from disk into internal object variables
- ``save_as()``: saves file to disk
- ``init_default()``: initializes file object with default information

Supported file types
--------------------

.. only:: latex

    .. code-block:: none

        *** Classes that can handle text files***
        FileAbXFwhm              : `x.py` Differential Abundances X FWHMs (Python source)
        FileAbonds               : PFANT Stellar Chemical Abundances
        FileAbsoru2              : PFANT "Absoru2" file
        FileAtoms                : PFANT Atomic Lines
        FileConfigConvMol        : Configuration file for molecular lines conversion GUI (Python code)
        FileDissoc               : PFANT Stellar Dissociation Equilibrium Information
        FileHmap                 : PFANT Hydrogen Lines Map
        FileKuruczMolecule       : Kurucz molecular lines file
        FileKuruczMolecule1      : Kurucz molecular lines file following format of file "c2dabrookek.asc"
        FileKuruczMoleculeBase   : Base class for the two types of Kurucz molecular lines file
        FileKuruczMoleculeOld    : Kurucz molecular lines file, old format #0
        FileKuruczMoleculeOld1   : Kurucz molecular lines file, old format #1
        FileMain                 : PFANT Main Stellar Configuration
        FileModTxt               : MARCS Atmospheric Model (text file)
        FileMolConsts            : Molecular constants config file (Python code)
        FileMolecules            : PFANT Molecular Lines
        FileOpa                  : MARCS ".opa" (opacity model) file format.
        FileOptions              : PFANT Command-line Options
        FilePar                  : WebSim-COMPASS ".par" (parameters) file
        FilePartit               : PFANT Partition Function
        FilePlezTiO              : Plez molecular lines file, TiO format
        FilePy                   : Configuration file saved as a .py Python source script
        FilePyConfig             : Base class for config files. Inherit and set class variable 'modulevarname' besides usual
        FileSpectrum             : Base class for all files representing a single 1D spectrum
        FileSpectrumNulbad       : PFANT Spectrum (`nulbad` output)
        FileSpectrumPfant        : PFANT Spectrum (`pfant` output)
        FileSpectrumXY           : "Lambda-flux" Spectrum (2-column text file)
        FileTRAPRBInput          : Input file for the TRAPRB Fortran code (which calculates Franck-Condon factors)
        FileTRAPRBOutput         : Output file for the TRAPRB Fortran code (which calculates Franck-Condon factors)
        FileToH                  : PFANT Hydrogen Line Profile
        FileVald3                : VALD3 atomic or molecular lines file

        *** Classes that can handle binary files***
        FileFullCube             : FITS WebSim Compass Data Cube
        FileHitranDB             : HITRAN Molecules Catalogue
        FileModBin               : PFANT Atmospheric Model (binary file)
        FileMolDB                : Database of Molecular Constants
        FileMoo                  : Atmospheric model or grid of models (with opacities included)
        FileSQLiteDB             : Represents a SQLite database file.
        FileSparseCube           : FITS Sparse Data Cube (storage to take less disk space)
        FileSpectrumFits         : FITS Spectrum
        FileSpectrumList         : FITS Spectrum List
        FileGalfit               : FITS file with frames named INPUT_*, MODEL_*, RESIDUAL_* (Galfit software output)

        *** Classes that can handle 1D spectrum files***
        FileSpectrum             : Base class for all files representing a single 1D spectrum
        FileSpectrumFits         : FITS Spectrum
        FileSpectrumNulbad       : PFANT Spectrum (`nulbad` output)
        FileSpectrumPfant        : PFANT Spectrum (`pfant` output)
        FileSpectrumXY           : "Lambda-flux" Spectrum (2-column text file)


    By the way, the table above was generated with the following code:

    .. literalinclude:: ../examples/f311/print-collaboration.py


.. only:: html

    .. |br| raw:: html

       <br />


    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | Description                                             | Default filename   | Class name             | Editors                        |
    +=========================================================+====================+========================+================================+
    | "Lambda-flux" Spectrum (2-column text file)             |                    | FileSpectrumXY         | ``splisted.py``                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | Atmospheric model or grid of models (with opacities     | grid.moo           | FileMoo                |                                |
    | |br| included)                                          |                    |                        |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | Configuration file for molecular lines conversion GUI   | configconvmol.py   | FileConfigConvMol      |                                |
    | |br| (Python code)                                      |                    |                        |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | Database of Molecular Constants                         | moldb.sqlite       | FileMolDB              | ``convmol.py``, ``moldbed.py`` |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | FITS Sparse Data Cube (storage to take less disk space) | default.sparsecube | FileSparseCube         |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | FITS Spectrum                                           |                    | FileSpectrumFits       | ``splisted.py``                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | FITS Spectrum List                                      | default.splist     | FileSpectrumList       | ``splisted.py``                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | FITS WebSim Compass Data Cube                           | default.fullcube   | FileFullCube           | ``cubeed.py``                  |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | FITS file with frames named INPUT_*, MODEL_*,           |                    | FileGalfit             |                                |
    | |br| RESIDUAL_* (Galfit software output)                |                    |                        |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | File containing Franck-Condon Factors (FCFs)            |                    | FileFCF                |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | HITRAN Molecules Catalogue                              | hitrandb.sqlite    | FileHitranDB           |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | Kurucz molecular lines file                             |                    | FileKuruczMolecule     |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | Kurucz molecular lines file, old format #0              |                    | FileKuruczMoleculeOld  |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | Kurucz molecular lines file, old format #1              |                    | FileKuruczMoleculeOld1 |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | MARCS ".opa" (opacity model) file format.               | modeles.opa        | FileOpa                |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | MARCS Atmospheric Model (text file)                     |                    | FileModTxt             |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | Molecular constants config file (Python code)           | configmolconsts.py | FileMolConsts          | ``mced.py``                    |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT "Absoru2" file                                    | absoru2.dat        | FileAbsoru2            |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT Atmospheric Model (binary file)                   | modeles.mod        | FileModBin             |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT Atomic Lines                                      | atoms.dat          | FileAtoms              | ``ated.py``                    |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT Command-line Options                              | options.py         | FileOptions            | ``x.py``                       |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT Hydrogen Line Profile                             | thalpha            | FileToH                |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT Hygrogen Lines Map                                | hmap.dat           | FileHmap               |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT Main Stellar Configuration                        | main.dat           | FileMain               | ``mained.py``, ``x.py``        |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT Molecular Lines                                   | molecules.dat      | FileMolecules          | ``mled.py``                    |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT Partition Function                                | partit.dat         | FilePartit             |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT Spectrum (`nulbad` output)                        |                    | FileSpectrumNulbad     | ``splisted.py``                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT Spectrum (`pfant` output)                         | flux.norm          | FileSpectrumPfant      | ``splisted.py``                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT Stellar Chemical Abundances                       | abonds.dat         | FileAbonds             | ``abed.py``, ``x.py``          |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | PFANT Stellar Dissociation Equilibrium Information      | dissoc.dat         | FileDissoc             |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | Plez molecular lines file, TiO format                   |                    | FilePlezTiO            |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | VALD3 atomic or molecular lines file                    |                    | FileVald3              |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | WebSim-COMPASS ".par" (parameters) file                 |                    | FilePar                |                                |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+
    | `x.py` Differential Abundances X FWHMs (Python source)  | abxfwhm.py         | FileAbXFwhm            | ``x.py``                       |
    +---------------------------------------------------------+--------------------+------------------------+--------------------------------+



    Here is the code which was used to generate the table above:

    .. code-block:: python

        import f311.filetypes as ft
        print("\n".join(ft.tabulate_filetypes_rest(description_width=55)))


Examples
--------

Convert 1D spectral file to FITS format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../docs/examples/filetypes/convert-to-fits.py


Import Kurucz' molecular linelist file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../docs/examples/filetypes/import-kurucz.py

.. code-block:: none

    KuruczMolLine(lambda_=2877.558,
                  loggf=-14.533,
                  J2l=23.0,
                  E2l=2354.082,
                  Jl=24.0,
                  El=37095.578,
                  atomn0=6,
                  atomn1=6,
                  state2l='a',
                  v2l=0,
                  lambda_doubling2l='e',
                  spin2l=1,
                  statel='d',
                  vl=10,
                  lambda_doublingl='e',
                  spinl=3,
                  iso=12)

