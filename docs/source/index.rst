f311 -- Python Astronomy resources
==================================

Project f311 is a collection of Astronomy-related packages and standalone applications written in Python.

This project started in 2015 at IAG-USP (Institute of Astronomy, Geophysics and Atmospheric Sciences at University of São Paulo, Brazil).
It has grown based on our daily needs, so we don't intend to be throughout in any of the topics covered, but we hope that you will find it useful.

Here is a list of f311 subpackages and their topics. 

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

f311 requires Python 3.x (Python 2 no longer supported due to maintainability issues, sorry).

Knowing the mess with different ecosystems and extant package versions, we provide four different installation methods.

Method 1

Try to install everything with pip:

.. code:: shell

   pip install a99 numpy scipy matplotlib astropy configobj bs4 robobrowser requests fortranformat tabulate rows
   pip install pyqt5
   pip install f311


If pyqt5 fails to install with pip, an alternative is to use apt-get:

.. code:: shell

   sudo apt-get install python3-PyQt5


**Note** You may need superuser rights (``sudo``) to install the packages above.

**Note** You may have to replace ``pip`` with ``pip3`` depending on your environment.


Method 2
^^^^^^^^

Use this method if you prefer to use Debian-based Linux packaging.

.. code:: shell

   sudo apt-get install python3-matplotlib python3-scipy python3-PyQt5 python3-astropy python3-pip python3-bs4
   sudo pip3 install a99 configobj robobrowser fortranformat tabulate # Requirements not in apt repository rows
   sudo pip3 install f311

Method 3
^^^^^^^^

This method uses a **conda** virtual environment. It works with a separate installation of Python and related packages.

First you will need to have Anaconda or Miniconda installed. If you have none of these installed yet, just install Miniconda.

Once Anaconda/Miniconda is installed, create a new virtual environment called "astroenv" (or any name you like):

.. code:: shell

   conda create --name astroenv python=3.5

Activate this new virtual environment:

.. code:: shell

   source activate astroenv

Now you should be able to install everything using pip:

.. code:: shell

   pip install a99 numpy scipy matplotlib astropy configobj pyqt5 bs4 robobrowser requests fortranformat tabulate rows
   pip install f311

**Note** Every time you want to work with _f311_, you will need to activate the environment:

.. code:: shell

   source activate astroenv

To deactivate the environment:

.. code:: shell

   source deactivate

Method 4 (developer mode)
^^^^^^^^^^^^^^^^^^^^^^^^^

This method is intended for developers or if you would like to pull overnight f311 versions instead of the pip version.

First install all required packages using either Method 1/2/3 above (but do not install f311).

To install f311 package, clone the GitHub repository:

.. code:: shell

   git clone ssh://git@github.com/trevisanj/f311.git

or

.. code:: shell

   git clone http://github.com/trevisanj/f311

Then, install in **developer** mode:

.. code:: shell

   cd f311
   python setup.py develop
   
**Note** The command above may vary having the ``sudo`` and/or ``python3`` flavor.


Troubleshooting installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MatPlotLib and PyQt5
^^^^^^^^^^^^^^^^^^^^

.. code:: shell

   ValueError: Unrecognized backend string "qt5agg": valid strings are ['GTKAgg', 'template', 'pdf',
   'GTK3Agg', 'cairo', 'TkAgg', 'pgf', 'MacOSX', 'GTK', 'WX', 'GTKCairo', 'Qt4Agg', 'svg', 'agg',
   'ps', 'emf', 'WebAgg', 'gdk', 'WXAgg', 'CocoaAgg', 'GTK3Cairo']

**Solution**: update Matplotlib to version 1.4 or later

Problems with package bs4
^^^^^^^^^^^^^^^^^^^^^^^^^

TODO


More
----

* :ref:`genindex` (all symbols listed alphabetically)
* :ref:`modindex` (whole *f311* package tree)
* :ref:`search`
* :doc:`license`

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

