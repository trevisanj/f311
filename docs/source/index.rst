Project *f311*
==============

Collection of Astronomy-related packages written in Python.

Spectral synthesis example:

.. code:: python

   import f311.pyfant as pf
   import f311.explorer as ex
   obj = pf.Pfant()
   obj.run()
   obj.load_result()
   ex.plot_spectra([obj.result["cont"], obj.result["spec"], obj.result["norm"]])


Sub-packages
--------

.. toctree::
   :maxdepth: 1

   pyfant
   convmol
   explorer
   filetypes
   physics
   aosss

Installation
------------

Required Software
~~~~~~~~~~~~~~~~~

- Python 3.xx

Python packages
^^^^^^^^^^^^^^^
- a99
- matplotlib
- scipy
- numpy
- astropy
- configobj
- tabulate
- fortranformat

Optional packages (functionality will be limited without them):

- PyQt5
- bs4
- robobrowser
- requests
- rows

Install
~~~~~~~

Method 1 (prefer _pip_, use _apt_ package as alternative)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: shell

   pip install a99 numpy scipy matplotlib astropy configobj bs4 robobrowser requests fortranformat tabulate rows
   pip install pyqt5
   pip install f311


**Note** You may need superuser rights (``sudo``) to install the packages above.

**Note** You may have to replace ``pip`` with ``pip3`` depending on your environment.

If _PyQt5_ fails to install with _pip_:

.. code:: shell

   sudo apt-get install python3-PyQt5

Method 2 (prefer _apt_, use _pip_ if no _apt_ package available)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: shell

   sudo apt-get install python3-matplotlib python3-scipy python3-PyQt5 python3-astropy python3-pip python3-bs4
   sudo pip3 install a99 configobj robobrowser fortranformat tabulate # Requirements not in apt repository rows
   sudo pip3 install f311

Method 3 (virtual environment with _conda_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This may be an alternative if you want to work with a separate installation of Python and related packages.
Here you need to have _Anaconda_ or _Miniconda_ installed.

Create a new virtual environment called "astroenv" (or any name you like):

.. code:: shell

   conda create --name astroenv python=3.5

Activate this new virtual environment:

.. code:: shell

   source activate astroenv

Now you should be able to install _f311_ from _pip_:

.. code:: shell

   pip install a99 numpy scipy matplotlib astropy configobj pyqt5 bs4 robobrowser requests fortranformat tabulate rows
   pip install f311

**Note** Every time you want to work with _f311_, you will need to activate the environment:

.. code:: shell

   source activate astroenv

To deactivate the environment:

.. code:: shell

   source deactivate

Method 4 (development mode)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Clone repository:

.. code:: shell

   git clone ssh://git@github.com/trevisanj/f311.git

or

.. code:: shell

   git clone http://github.com/trevisanj/f311

Install in **developer** mode:

.. code:: shell

   cd f311
   sudo python3 setup.py develop


Installation troubleshooting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   ValueError: Unrecognized backend string "qt5agg": valid strings are ['GTKAgg', 'template', 'pdf',
   'GTK3Agg', 'cairo', 'TkAgg', 'pgf', 'MacOSX', 'GTK', 'WX', 'GTKCairo', 'Qt4Agg', 'svg', 'agg',
   'ps', 'emf', 'WebAgg', 'gdk', 'WXAgg', 'CocoaAgg', 'GTK3Cairo']

**Solution**: update Matplotlib to version 1.4 or later




More
----

* :ref:`genindex` (all symbols listed alphabetically)
* :ref:`modindex` (whole *f311* package tree)
* :ref:`search`
* :doc:`license`
