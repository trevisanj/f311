Spectral synthesis (``f311.pyfant``)
====================================

Welcome!!

pyfant is a Python interface for the `PFANT Spectral Synthesis
Software <http://trevisanj.github.io/PFANT>`__ for Astronomy.


Spectral synthesis softwares have a fundamental role in Astronomy.
It is a crucial step in determining stellar properties
- such as temperature, metallicity, and chemical abundances -
in which the synthetic spectrum (or a combination of several of these) is compared with the
measured spectrum of a star or a whole stellar population either by the full spectrum fitting,
spectral energy distribution or specific spectral lines and regions.
It is of great interest that the software has a comprehensive and intuitive user interface and
easiness of parameter input and its multiple variations, and also tools for incorporating data
like atomic/molecular lines, atmospheric models, etc.

Applications
------------

The applications related to package f311.pyfant are listed below. For them to work, you need to
`install PFANT <http://trevisanj.github.io/PFANT/install.html>`_.

The `PFANT Quick Start <http://trevisanj.github.io/PFANT/quick.html>`_ serves as a guide to
using these applications.

Graphical applications
~~~~~~~~~~~~~~~~~~~~~~

- ``x.py`` -- PFANT Launcher -- Graphical Interface for Spectral Synthesis

Command-line tools
~~~~~~~~~~~~~~~~~~

- ``copy-star.py`` -- Copies stellar data files (such as main.dat, abonds.dat, dissoc.dat) to local directory
- ``link.py`` -- Creates symbolic links to PFANT data files as an alternative to copying these (sometimes large) files into local directory
- ``run4.py`` -- Runs the four Fortran binaries in sequence: ``innewmarcs``, ``hydro2``, ``pfant``, ``nulbad``
- ``save-pdf.py`` -- Looks for files "*.norm" inside directories session-* and saves one figure per page in a PDF file


Coding using the API
--------------------

Spectral synthesis
~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../examples/synthesis-simple/synthesis-simple.py

.. figure:: ../figures/norm-convolved.png
   :align: center

Continuum
~~~~~~~~~

.. literalinclude:: ../examples/synthesis-simple/synthesis-continuum.py

.. figure:: ../figures/continuum.png
   :align: center

Plot hydrogen profiles
~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../examples/plot-hydrogen-profiles/plot-hydrogen-profiles.py

.. figure:: ../figures/hydrogen-profiles.png
   :align: center

API reference
-------------

:doc:`autodoc/f311.pyfant`
