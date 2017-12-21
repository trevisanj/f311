F311 Installation
=================

Package ``f311`` can be installed using the following command on your shell::

    pip install f311

If the above fails, or you had a different installation procedure in mind,
you may find more useful information below.

Method 1: Using Anaconda without virtual environment
----------------------------------------------------

This will make Anaconda's Python 3 the default ``python`` command for your user account.
Make sure you don't mind this, otherwise follow Method 2.

First install Anaconda or Miniconda. When you do so, please make sure that you **answer "yes" to this (or similar) question**::

    Do you wish the installer to prepend the Miniconda3 install location
    to PATH in your /home/j/.bashrc ? [yes|no]
    >> yes


After Anaconda/Miniconda installation, close the terminal and open it again so that your PATH is updated.
**Or if your shell is bash**, you can just type ``source ~/.bashrc`` on the terminal.

Now install package ``f311`` using pip::

   pip install f311

Method 2: Using Anaconda virtual environment
--------------------------------------------

This method uses a **conda** virtual environment. It works with a separate installation of Python and related packages.

First you will need to have Anaconda or Miniconda installed. If you have none of these installed yet, just install Miniconda.

Once Anaconda/Miniconda is installed, create a new virtual environment called "astroenv" (or any name you like):

.. code:: shell

   conda create --name astroenv python=3.5 # or 3.6

Activate this new virtual environment:

.. code:: shell

   source activate astroenv

Now install package ``f311``:

.. code:: shell

   pip install f311

**Note** Every time you want to work with F311, you will need to activate the environment:

.. code:: shell

   source activate astroenv

To deactivate the environment:

.. code:: shell

   source deactivate

Method 3: Developer mode
------------------------

This option allows you to download and modify the source code.


Clone the f311 GitHub repository:

.. code:: shell

   git clone ssh://git@github.com/trevisanj/f311.git

or

.. code:: shell

   git clone http://github.com/trevisanj/f311

Finally, install F311 in **developer** mode:

.. code:: shell

   cd f311
   python setup.py develop

Upgrade ``f311``
----------------

Pacakge ``f311`` can be upgraded to a new version by typing::

    pip install f311 --upgrade


Package dependencies
--------------------

``f311`` package dependencies are listed below. This list is provided only for reference, as **these
packages should be automatically installed** during the installation process.

- numpy
- scipy
- matplotlib
- astropy
- configobj
- bs4
- lxml
- robobrowser
- requests
- fortranformat
- tabulate
- rows
- pyqt5
- a99

Troubleshooting installation
----------------------------

This section shows some possible errors and their solutions.

Python version and release
~~~~~~~~~~~~~~~~~~~~~~~~~~

``f311`` was designed to run with Python 3 (Python 2 support has been discontinued).

Furthermore, in order to install correctly using the ``pip`` command, the Python release needs to be either
Python 3.4.6+, Python 3.5.3+, or Python 3.6+ (according to https://packaging.python.org/guides/migrating-to-pypi-org/).


MatPlotLib and PyQt5
~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   ValueError: Unrecognized backend string "qt5agg": valid strings are ['GTKAgg', 'template', 'pdf',
   'GTK3Agg', 'cairo', 'TkAgg', 'pgf', 'MacOSX', 'GTK', 'WX', 'GTKCairo', 'Qt4Agg', 'svg', 'agg',
   'ps', 'emf', 'WebAgg', 'gdk', 'WXAgg', 'CocoaAgg', 'GTK3Cairo']

**Solution**: upgrade Matplotlib to version 1.4 or later

Problems with package bs4
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

  bs4.FeatureNotFound: Couldn't find a tree builder with the features you requested: lxml. Do you need to install a parser library?

**Solution**: install package "lxml"::

    pip install lxml

Other problems
~~~~~~~~~~~~~~
If you have other installation problems or have a suggestion, please open an issue at the project
site on `GitHub <http://github.com/trevisanj/f311>`_.