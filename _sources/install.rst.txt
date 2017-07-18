f311 Installation
=================

f311 requires Python 3.x. It also depends on other packages, but
the installation of these is included in the instructions below.

Four different installation methods are described below:

Method 1: Using pip
-------------------

To install f311 with pip, run:

.. code:: shell

   pip install numpy scipy matplotlib astropy configobj bs4 robobrowser requests fortranformat tabulate rows pyqt5 a99 f311

If pyqt5 fails to install with pip, an alternative is to use ``apt-get``:

.. code:: shell

   sudo apt-get install python3-PyQt5


**Note** You may need superuser rights (``sudo``) to install the packages above.

**Note** You may have to replace ``pip`` with ``pip3`` depending on your environment.


Method 2: Using apt-get
-----------------------

Use this method if you prefer to use Debian-based Linux packaging.

.. code:: shell

   sudo apt-get install python3-matplotlib python3-scipy python3-PyQt5 python3-astropy python3-pip python3-bs4
   sudo pip3 install a99 configobj robobrowser fortranformat tabulate # Requirements not in apt repository rows
   sudo pip3 install f311

Method 3: Using Anaconda virtual environment
--------------------------------------------

This method uses a **conda** virtual environment. It works with a separate installation of Python and related packages.

First you will need to have Anaconda or Miniconda installed. If you have none of these installed yet, just install Miniconda.

Once Anaconda/Miniconda is installed, create a new virtual environment called "astroenv" (or any name you like):

.. code:: shell

   conda create --name astroenv python=3.5 # or 3.6

Activate this new virtual environment:

.. code:: shell

   source activate astroenv

Now you should be able to install all the packages using pip:

.. code:: shell

   pip install numpy scipy matplotlib astropy configobj bs4 robobrowser requests fortranformat tabulate rows pyqt5 a99 f311

**Note** Every time you want to work with _f311_, you will need to activate the environment:

.. code:: shell

   source activate astroenv

To deactivate the environment:

.. code:: shell

   source deactivate

Method 4: Using Anaconda without virtual environment
----------------------------------------------------

This will make Anaconda's Python 3 the default Python for your user account. Make sure you are OK with this.

When you install Anaconda/Miniconda, answer yes to this (or similar) question::

    Do you wish the installer to prepend the Miniconda3 install location
    to PATH in your /home/j/.bashrc ? [yes|no]


After Anaconda/Miniconda installation, close the terminal and open it again so that your PATH is updated.
**Or if your shell is bash**, you can just type ``source ~/.bashrc`` on the terminal.

Now the packages:

.. code:: shell

   pip install numpy scipy matplotlib astropy configobj bs4 robobrowser requests fortranformat tabulate rows pyqt5 a99 f311


Method 5: Developer mode
------------------------

This method is intended for developers or if you would like to pull overnight f311 versions instead of the pip version.

First install all required packages using either Method 1/2/3/4 above (but do not install f311).

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
----------------------------

MatPlotLib and PyQt5
~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   ValueError: Unrecognized backend string "qt5agg": valid strings are ['GTKAgg', 'template', 'pdf',
   'GTK3Agg', 'cairo', 'TkAgg', 'pgf', 'MacOSX', 'GTK', 'WX', 'GTKCairo', 'Qt4Agg', 'svg', 'agg',
   'ps', 'emf', 'WebAgg', 'gdk', 'WXAgg', 'CocoaAgg', 'GTK3Cairo']

**Solution**: update Matplotlib to version 1.4 or later

Problems with package bs4
~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo:: There is an error that occurs with package bs4 of easy fix, let's write it here at next chance to observe it.
