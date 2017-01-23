# Package pyperdrive

This is an infra-structure to build Python applications for Astronomy (or not):

  - Data file framework
  - GUI development (PyQt5)
  - Astronomy/Physics-related resources
  - Script indexing
  - Miscellanea

#### Data file framework

  - Plugin-like framework to implement readig/writing/visualization for new file types
  - Automatic file type detection by def `load_any_file()`
  - Explore files using `explorer.py`
  - Already supports 1D spectra (including FITS format)
  - Base class `FilePy` supports Python sources as config files
  - Base class `FileLiteDB` wraps a SQLite3 database
  
#### GUI development (PyQt5)

  - Widgets
  - Windows
  - Python syntax highlighter
  - Window placement in desktop
  - Widget formatting

#### Astronomy/Physics-related resources

  - Photometry (AB/Vega/Standard)
  - Spectrum-to-RGB color conversion
  - Air-to-vacuum and _vice versa_ wavelenght conversion
  - Calculation of Hönl-London factors according to formulas in Kovács' 1969 [1] 
  - Command-line tools to plot and cut spectra

#### Script indexing

  - `programs.py`: lists all programs/applications/scripts from included `hypydrive` and
    "collaborator" projects

#### Miscellanea

  - Subclass of `configobj.ConfigObj`
  - Work with SQLite3 databases
  - Introspection
  - Logging
  - Matplotlib
  - Text interface
  - Many conversion routines
  - File I/O
  - Searches
  - Random person name generator

## Examples

### Air-to-vacuum (& vice versa) wavelength conversion

The following code reproduces the figure shown in VALD3 Wiki (http://www.astro.uu.se/valdwiki/Air-to-vacuum%20conversion)
("comparison of the Morton and the inverse transformation by NP between 2000 Å and 100000 Å.")

```python
import matplotlib.pyplot as plt
import numpy as np
import pyperdrive as pp
λvac = 10**np.linspace(np.log10(2000), np.log10(1000000), 2000)
y = pp.air_to_vacuum(pp.vacuum_to_air(λvac))-λvac
plt.semilogx(λvac, y)
plt.xlabel("$\lambda$ in Angstroem")
plt.ylabel("$\Delta\lambda$")
plt.xlim([λvac[0]-50, λvac[-1]])
plt.title("air_to_vacuum(vacuum_to_air($\lambda_{vac}$))-$\lambda_{vac}$")
plt.tight_layout()
plt.show()
```

![](air-vac.png)

### Flux-to-magnitude conversion

The following example compares flux-to-magnitude conversion of the Vega spectrum
for different magnitude systems.

```python
import pyperdrive as pp
import tabulate
systems = ["stdflux", "ab", "vega"]
bands = "UBVRIJHK"
sp = pp.get_vega_spectrum()
rows = [([band]+[pp.calc_mag(sp, band, system) for system in systems]) for band in bands]
print(tabulate.tabulate(rows, ["band"]+systems))
```

Result:

```
band        stdflux          ab    vega
------  -----------  ----------  ------
U        0.00572505   0.761594       -0
B        0.0696287   -0.10383        -0
V        0.0218067    0.0191189      -0
R        0.0359559    0.214645       -0
I        0.0661095    0.449825       -0
J       -0.0150993    0.874666       -0
H        0.0315447    1.34805        -0
K        0.0246046    1.85948        -0
```