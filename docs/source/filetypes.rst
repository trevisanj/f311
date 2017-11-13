File handling API (``f311.filetypes``)
======================================

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

The following table was generated in 12/Nov/2017. The "Editor" column shows the applications in
the F311 project that can handle these files (*i.e.*, load/edit/save).

All file types are also recognized by ``explorer.py``.


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



By the way, the above table was generated with the following code:

.. code-block:: python

    import filetypes as ft
    print("\n".join(ft.tabulate_filetypes_rest(55)))

Examples
--------

Convert 1D spectral file to FITS format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../docs/examples/filetypes/convert-to-fits.py

API reference
-------------

:doc:`autodoc/f311.filetypes`

