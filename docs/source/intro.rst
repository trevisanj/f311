Introduction
============

Project F311 encompasses a range of resources on selected Astronomy-related topics.

F311 installs as a package for Python 3, thereby making available several
GUI (graphical user interface) and command-line applications,
and their accompanying Python APIs (application programming interfaces).

The project is organized in sub-packages, whose main roles are related below:

- :doc:`Package f311.pyfant <pyfant>` is a Python interface to the
  `PFANT <trevisanj.github.io/PFANT>`_ spectral synthesis Fortran code,
  containing the "PFANT launcher" application that can run several spectral synthesis "jobs"
  in parallel, and an API to create complex applications involving spectral synthesis.
- :doc:`Package f311.convmol <convmol>` provides a GUI application to browse and edit a molecular constants database,
  and allows conversion of molecular linelists from several formats available to the PFANT format.
- :doc:`Package f311.explorer <explorer>` contains most of the GUIs of the project, with a file-explorer-like application,
  GUI editors for several Astronomy-related file types, several visualization options for these files,
  and command-line tools to cut data files to a spectral range of interest, merge molecular
  inelists in a single file, etc.
- :doc:`Package f311.filetypes <filetypes>` is an object-oriented, plugin-based API to load and save more than 40
  different file formats used in astronomy, including some FITS files structures, and most file
  types used by the PFANT software.
- :doc:`Package f311.physics <physics>` provides an API on the following topics: photometry calculations,
  air-to-vacuum wavelength conversions, and calculation of molecular line strengths
  (Hönl-London factors) according to [Kovacs1969]_.
- :doc:`Package f311.aosss <aosss>` provides a set of tools related to the E-ELT/MOSAIC spectrograph.
  More specifically, it was designed to organize and manipulate the set of output files generated
  by the `WebSim-COMPASS <http://websim-compass.obspm.fr/>`_ simulator of that spectrograph.


After installed, it is possible to run the script ``programs.py`` to list all the applications
included in the project.

Using the API
-------------

One or more of the subpackages can be imported as follows:

.. code::

    import f311.pyfant as pf
    import f311.convmol as cm
    import f311.explorer as ex
    import f311.filetypes as ft
    import f311.physics as ph
    import f311.aosss as ao

Or alternatively (all symbols from all subpackages exposes in ``f311`` namespace),

.. code::

    import f311

Contributing to this project
----------------------------

Project F311 on `GitHub <https://github.com/trevisanj/f311>`_.

Acknowledgement
---------------

The project started in 2015 at IAG-USP (Institute of Astronomy, Geophysics and Atmospheric Sciences
at University of São Paulo, Brazil).

Partially funded by FAPESP - Research Support Foundation of the State of São Paulo, Brazil (2015-2017).

.. only:: html

    Bibliography
    ------------

.. [Kovacs1969] Istvan Kovacs, Rotational Structure in the spectra of diatomic molecules.
   American Elsevier, 1969.