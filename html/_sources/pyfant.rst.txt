*f311.pyfant*: spectral synthesis
=================================

Welcome!!

pyfant is a Python interface for the `PFANT Spectral Synthesis
Software <http://github.com/trevisanj/PFANT>`__ for Astronomy.

Apart from spectral synthesis, it provides tools of conversion, data
editing, and visualization, and a programming library to embed spectral
synthesis into your code.

Introduction
------------

The *pyfant* Python package was created as a Python interface for
PFANT, a Fortran-developed Spectral Synthesis Software for Astronomy
(http://github.com/trevisanj/PFANT).

Spectral Synthesis Softwares (SSS) have several applications in
Astronomy. Spectral synthesis is a crucial step in optimization
algorithms, in which the synthetic spectrum is compared with the measure
spectrum of a star, in order to determine stellar properties -- such as
temperature, metallicity, and chemical abundances -- in an iterative
fashion.

*pyfant* was first created with the intention to provide an
object-oriented library to develop such algorithms in Python. It allows
one to create several "spectral synthesis cases" (*e.g.* similar
calculations where only the chemical abundance of one element will vary
slightly) and run these cases in parallel.

The package is now part of the *f311* project, which contains tools to
carry out many related tasks: - editors for many of the file types
involved - plotting tools - conversion of atomic and molecular lines
from/to standards from other research groups

Applications Available
----------------------

.. code:: shell

    programs.py -p pyfant markdown-list

Graphical applications:

- `x.py` -- PFANT Launcher -- Graphical Interface for Spectral Synthesis

Command-line tools:

- `copy-star.py` -- Copies stellar data files (such as main.dat, abonds.dat, dissoc.dat) to local directory

- `link.py` -- Creates symbolic links to PFANT data files as an alternative to copying these (sometimes large) files into local directory

- `run4.py` -- Runs the four Fortran binaries in sequence: `innewmarcs`, `hydro2`, `pfant`, `nulbad`

- `save-pdf.py` -- Looks for files "*.norm" inside directories session-* and saves one figure per page in a PDF file


Using *pyfant* applications
---------------------------

The *pyfant* application guide is currently part of the PFANT manual at
http://github.com/trevisanj/PFANT


API reference
-------------

:doc:`autodoc/f311.pyfant`
