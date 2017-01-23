# Package **pyfant**: spectral synthesis & handling of related data types

Welcome!!

pyfant is a Python interface for the 
[PFANT Spectral Synthesis Software](http://github.com/trevisanj/PFANT)
for Astronomy.

Apart from spectral synthesis, it provides tools of conversion, data editing,
and visualization, and a programming library to embed spectral synthesis into your code.

# Table of contents

  1. [Introduction](#S1)
  2. [Installation](#S2)
  3. [Handled file types](#S3)
  4. [Tasks](#S4)
  5. [Programming with `pyfant`](#S5)
  6. [Troubleshooting](#S6)


# <a name=S1></a>1 Introduction

The `pyfant` Python package was created as a Python interface for PFANT, a Fortran-developed
Spectral Synthesis Software for Astronomy (http://github.com/trevisanj/PFANT).

`pyfant` was first created with the intention to provide an object-oriented library to develop such
algorithms in Python. It allows one to create several "spectral synthesis cases" (_e.g._ similar
calculations where only the chemical abundance of one element will vary slightly) and run these cases
in parallel.

The package has since evolved to provide graphical and command-line applications to perform
many convenient tasks:
  - editors for many of the file types involved
  - plotting tools
  - conversion of atomic and molecular lines from/to standards from other research groups

#<a name=S2></a>2. Installation

TO install _package `pyfant`, please follow [installation instructions for _astrogear_](../README.md)

# <a name=S3></a>3 Applications Available

:bulb: To print a list of all command-line tools, run `programs.py`

Graphical applications:
  - `abed.py` -- Abundances file editor
  - `ated.py` -- Atomic lines file editor
  - `cubeed.py` -- Data Cube Editor
  - `explorer.py` -- PFANT Explorer --  list, visualize, and edit data files (_à la_ File Manager)
  - `mained.py` -- Main configuration file editor
  - `mled.py` -- Molecular lines file editor
  - `splisted.py` -- FileSpectrumList editor with import/export FileFullCube
  - `tune-zinf.py` -- Tunes the zinf parameter for each atomic line in atomic lines file.
  - `x.py` -- PFANT Launcher

Command-line tools:
  - `copy-_star.py` -- Copies stellar data files to local directory.
  - `create-grid.py` -- Model Grid Creator from MARCS atmospheric models 
  - `cut-atoms.py` -- Cuts atomic lines file to wavelength interval specified.
  - `cut-molecules.py` -- Cuts molecular lines file to wavelength interval specified.
  - `cut-spectrum.py` -- Cuts spectrum file to wavelength interval specified. Saved in 2-column format.
  - `link.py` -- Creates symbolic links to PFANT data files as an alternative to copying these (sometimes large) files into local directory.
  - `plot-spectra.py` -- Plot spectra to screen or PDF.
  - `programs.py` -- Lists all Fortran/Python programs available (PFANT + pyfant).
  - `run4.py` -- Runs the four Fortran binaries in sequence: innewmarcs, hydro2, pfant, nulbad.
  - `save-pdf.py` -- Looks for file "flux.norm" inside directories session-* and saves one figure per page in a PDF file.
  - `vald3-to-atoms.py` -- Converts VALD3 atomic/molecular lines file to PFANT atomic lines file.


# <a name=S4></a>4 Tasks

This section briefly describes some tasks that can be performed with `pyfant` applications.



## More examples

  - The _demos_ directory contains a few (non-exhaustive) examples of how
    to use pyfant to perform different tasks. [](demos/README.md).

  - [`run4.py` source code](scripts/run4.py)
  

