Browse, read, write, visualize, edit files (``f311.explorer``)
==============================================================

Introduction
------------

File edit & visualization, including file-explorer-like ``explorer.py`` (:numref:`figexplorer`).

.. _figexplorer:

.. figure:: ../figures/explorer.png
   :align: center

    -- ``explorer.py`` screenshot.


List of applications
--------------------

.. code:: shell

    programs.py -p explorer

Graphical applications:

- ``abed.py`` -- Abundances file editor

- ``ated.py`` -- Atomic lines file editor

- ``cubeed.py`` -- Data Cube Editor, import/export WebSim-COMPASS data cubes

- ``explorer.py`` -- F311 Explorer --  list, visualize, and edit data files (*à la* File Manager)

- ``mained.py`` -- Main configuration file editor.

- ``mled.py`` -- Molecular lines file editor.

- ``splisted.py`` -- Spectrum List Editor

- ``tune-zinf.py`` -- Tunes the "zinf" parameter for each atomic line in atomic lines file


Command-line tools:

- ``create-grid.py`` -- Merges several atmospheric models into a single file (_i.e._, the "grid")

- ``cut-atoms.py`` -- Cuts atomic lines file to wavelength interval specified

- ``cut-molecules.py`` -- Cuts molecular lines file to wavelength interval specified

- ``cut-spectrum.py`` -- Cuts spectrum file to wavelength interval specified

- ``plot-spectra.py`` -- Plots spectra on screen or creates PDF file

- ``vald3-to-atoms.py`` -- Converts VALD3 atomic/molecular lines file to PFANT atomic lines file.


API reference
-------------

:doc:`autodoc/f311.explorer`
