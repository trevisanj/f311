Conversion of molecular spectral lines (``f311.convmol``)
=========================================================

Introduction
------------

.. note:: This package is currently under construction (2017-04-18)

Cconversion between different formats of files containing molecular spectral lines data.

Conversion sources:

- Robert Kurucz molecular line lists (fully implemented (old and new Kurucz format))
- HITRAN Online database (partially implemented)
- VALD3 (to do)
- TurboSpectrum (to do)

Conversion destination:

- PFANT molecular lines format

Applications
------------

Graphical applications:

- ``convmol.py`` -- Conversion of molecular lines data to PFANT format

Command-line tools:

- ``hitran-scraper.py`` -- Retrieves molecular lines from the HITRAN database


- ``nist-scraper.py`` -- Retrieves molecular constants from NIST Web Book for a particular molecule

Usage Examples
--------------

- :doc:`hitran-scraper`
- :doc:`nist-scraper`
- :doc:`convmol-gui`


API reference
-------------

:doc:`autodoc/f311.convmol`
