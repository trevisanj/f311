*f311.pyfant*: spectral synthesis
=================================

Welcome!!

pyfant is a Python interface for the `PFANT Spectral Synthesis
Software <http://github.com/trevisanj/PFANT>`__ for Astronomy.

- run several spectral synthesis "jobs" in parallel using ``x.py``

- write your own spectral synthesis scripts using the ``f311.pyfant`` package

Spectral synthesis softwares have a fundamental role in Astronomy.
Spectral synthesis is a crucial step in determining stellar properties
- such as temperature, metallicity, and chemical abundances -
in which the synthetic spectrum (or a combination of several of these) is compared with the
measured spectrum of a star or a whole stellar population either by the full spectrum fitting,
spectral energy distribution or specific spectral lines and regions.
It is of great interest that the software has a comprehensive and intuitive user interface and
easiness of parameter input and its multiple variations, and also tools for incorporating data
like atomic/molecular lines, atmospheric models, etc.


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
