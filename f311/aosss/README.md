# aosss

Adaptive Optics Systems Simulation Support 

Welcome!

# Table of contents

  1. [Introduction](#S1)
  2. [Installation](#S2)
  3. [Usage Examples](#S3)


#<a name=S1></a>1 Introduction

`aosss` is a Python package and set of applications to facilitate 
steps in spectrograph+telescope simulation workflows: 

  - assemble a data cube for IFU simulation
  - batch-download simulations resulting files
  - organize resulting files
  - generate visual reports
  - compile results into *spectrum list files*
  - process/convert/visualize these *spectrum list files* 
  
## 1.1 Structure

`aosss` contains an API (application programming interface) and a set of scripts (standalone programs)
that use this API.

### 1.1.1 Programs available

:bulb: To print a list of `aosss` programs, run `programs.py` from the console:

Graphical applications:
  - `wavelength-chart.py` -- Draws a [wavelength] x [various stacked information] chart

Command-line tools:
  - `create-spectrum-lists.py` -- Create several .splist files, grouping spectra by their wavelength vector
  - `aosss-create-websim-report.py` -- Creates report for a given set of WEBSIM-COMPASS output files
  - `get-compass.py` -- Downloads a number of Websim-Compass simulations
  - `aosss-programs.py` -- Lists all programs available with `aosss` package

All the programs above can be called with the `--help` or `-h` option for more documentation

#<a name=S2></a>2. Installation

TO install _package `aosss`, please follow [installation instructions for _astrogear_](../README.md) 

#<a name=S3></a>3. Usage Examples

## 3.1 Download simulation results

```shell
aosss-get-compass.py 1206-1213
```

will download results for simulations *C001206*, *C001207*, ..., 
*C001213* **into the local directory**, after which you will see files
`C*.fits`, `C*.par`,  `C*.out`

## 3.2 Create reports

```shell
aosss-create-simulation-reports.py 1206-1213
```

creates **HTML** and **PNG** files, for instance:

```shell
$ ls report-C001206*
report-C001206-000.png  report-C001206-002.png  report-C001206-004.png  report-C001206-006.png  report-C001206-008.png  report-C001206.html
report-C001206-001.png  report-C001206-003.png  report-C001206-005.png  report-C001206-007.png  report-C001206-009.png
```

## 3.3 Group resulting spectra with same wavelength axis
  
The following will group all files `C*_spintg.fits` into different
**spectrum list files**. Each of these files will contain the spectra that
share the same wavelength axis.

```shell
aosss-create-spectrum-lists.py
```

## 3.4 Organize files

The following will move files into different directories according to
some rules:

```shell
$ aosss-organize-directory.py --help
usage: aosss-organize-directory.py [-h]

Performs a list of pre-defined tasks to organize a directory containing simulations:
  - moves 'root/report-*'       to 'root/reports'
  - moves 'root/C*'             to 'root/raw'
  - moves 'root/raw/simgroup*'  to 'root/'
  - moves 'root/raw/report-*'   to 'root/reports'
  - [re]creates 'root/reports/index.html'

This script can be run from one of these directories:
  - 'root' -- a directory containing at least one of these directories: 'reports', 'raw'
  - 'root/raw'
  - 'root/reports'

The script will use some rules to try to figure out where it is running from

optional arguments:
  -h, --help  show this help message and exit

$ aosss-organize-directory.py
. 
.
.
[INFO    ]   - Move 221 objects
[INFO    ]   - Create 'reports/index.html'
Continue (Y/n)? 

```

## 3.5 Browse through reports

```shell
cd reports
xdg-open index.html
```

will open file `index.html` in browser

[](doc/index-html.png)

## 3.6 Inspecting where spectral lines of interest will fall due to redshift

```shell
aosss-wavelength-chart.py
```

Lines with zero redshift:
![](doc/chart-z-0.png)

Lines with `z=3.5`:
![](doc/chart-z-35.png)
