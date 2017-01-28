*f311.explorer*: browse, read, write, visualize, edit files
=====

Introduction
------------

*explorer* provides applications and an API to handle many file format used in Astronomy.

Most resources are accessible through ``explorer.py`` (file-explorer-like application)

Applications
------------

.. code:: shell

    programs.py -p explorer markdown-list


Graphical applications:

- `abed.py` -- Abundances file editor

- `ated.py` -- Atomic lines file editor

- `cubeed.py` -- Data Cube Editor, import/export WebSim-COMPASS data cubes

- `explorer.py` -- AstroAPI Explorer --  list, visualize, and edit data files (_à la_ File Manager)

- `mained.py` -- Main configuration file editor.

- `mled.py` -- Molecular lines file editor.

- `splisted.py` -- Spectrum List Editor

- `tune-zinf.py` -- Tunes the "zinf" parameter for each atomic line in atomic lines file


Command-line tools:

- `create-grid.py` -- Merges several atmospheric models into a single file (_i.e._, the "grid")

- `cut-atoms.py` -- Cuts atomic lines file to wavelength interval specified

- `cut-molecules.py` -- Cuts molecular lines file to wavelength interval specified

- `cut-spectrum.py` -- Cuts spectrum file to wavelength interval specified

- `plot-spectra.py` -- Plots spectra on screen or creates PDF file

- `vald3-to-atoms.py` -- Converts VALD3 atomic/molecular lines file to PFANT atomic lines file.


All the programs above can be called with the ``--help`` or ``-h``
option for more information.

API reference
-------------

:doc:`autodoc/f311.explorer`
