F311 -- Python resources for Astronomy
======================================

Welcome to the F311 documentation!

.. toctree::
   :maxdepth: 1

   install
   pyfant
   convmol
   explorer
   filetypes
   physics
   aosss
   cheat

Introduction
------------

F311 is an Astronomy-related API, command-line tools, and windowed applications for Python 3.

Sub-packages: see menu on the left.

For a list of scripts (the following will print something :doc:`like this <programs-py-listing>`):

.. code:: shell

   programs.py

To use the APIs to write your own code, the f311 subpackages that can be imported like this:

.. code::

    import f311.pyfant as pf
    import f311.convmol as cm
    import f311.explorer as ex
    import f311.filetypes as ft
    import f311.physics as ph
    import f311.aosss as ao

Although the code is not throughout on the topics covered, some parts of the code were structured
to be comprehensively and easily expanded.

The project started in 2015 at IAG-USP (Institute of Astronomy, Geophysics and Atmospheric Sciences
at University of São Paulo, Brazil).

How to contribute
-----------------

There are several ways in which you can contribute to this project:

* Report a bug
* Give some suggestions feedback
* Write documentation
* Send examples
* Contribute with coding

If you would like to contribute to this project, please create a pull request on GitHub and/or drop an e-mail to juliotrevisan@gmail.com


Funding
-------

Funded by FAPESP - Research Support Foundation of the State of São Paulo, Brazil (2015-2017).

More
----

* :ref:`genindex` (all symbols listed alphabetically)
* :ref:`modindex` (whole f311 package tree)
* :ref:`search`
* :doc:`license`

.. todo:: Bring more examples and find a way to organize them both in the code and in the documentation
