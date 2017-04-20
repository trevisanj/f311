Conversion of molecular spectral lines (``f311.convmol``)
=========================================================

Introduction
------------

.. note:: This package is currently under construction (2017-04-18)

Package convmol contains an application to perform conversion between different molecular
spectral lines formats, some command-line tools, and an API based on which the applications
were constructed.

Conversion sources:

- HITRAN Online database
- Robert Kurucz molecular line lists
- VALD3
- TurboSpectrum

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
