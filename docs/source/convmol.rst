*f311.convmol*: Conversion of molecular spectral lines
=====

Introduction
------------

*convmol* provides resources to convert between different molecular spectral lines formats.

**This package is currently under development (2017-01-28)**

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

- ``convmol.py`` -- Converion of molecular lines data to PFANT format


Command-line tools:

- ``download-hitran.py`` -- Downloads molecular lines from HITRAN database (using "HITRAN API" backend)

- ``show-nist.py`` -- Downloads and prints molecular constants from NIST Web Book for a particular molecule


All the programs above can be called with the ``--help`` or ``-h``
option for more information.

API reference
-------------

:doc:`autodoc/f311.aosss`
