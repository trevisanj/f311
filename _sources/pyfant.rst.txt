*f311.pyfant*: spectral synthesis
=================================

Welcome!!

pyfant is a Python interface for the `PFANT Spectral Synthesis
Software <http://github.com/trevisanj/PFANT>`__ for Astronomy.

- run several spectral synthesis "jobs" in parallel using ``x.py``

- write your own spectral synthesis scripts using the ``f311.pyfant`` package

Spectral Synthesis Softwares (SSS) have several applications in
Astronomy. Spectral synthesis is a crucial step in optimization
algorithms, in which the synthetic spectrum is compared with the measure
spectrum of a star, in order to determine stellar properties -- such as
temperature, metallicity, and chemical abundances -- in an iterative
fashion.

Quick start
-----------

The following example Spectral synthesis example:

.. code:: python

   import f311.pyfant as pf
   import f311.explorer as ex
   obj = pf.Pfant()
   obj.run()
   obj.load_result()
   ex.plot_spectra([obj.result["cont"], obj.result["spec"], obj.result["norm"]])


Using *pyfant* applications
---------------------------

The *pyfant* application guide is currently part of the PFANT manual at
http://github.com/trevisanj/PFANT



API reference
-------------

:doc:`autodoc/f311.pyfant`
