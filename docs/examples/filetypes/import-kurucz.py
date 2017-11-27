"""
This example loads file "c2dabrookek.asc" and prints a memory representation of its first line.

This file can be obtained at http://kurucz.harvard.edu/molecules/c2/. First lines of file:

```
  287.7558-14.533 23.0  2354.082 24.0 -37095.578 6063a00e1  3d10e3  12 677  34741.495
  287.7564-14.955 22.0  2282.704 23.0 -37024.124 6063a00f1  3d10f3  12 677  34741.419
  287.7582-14.490 21.0  2214.696 22.0 -36955.900 6063a00e1  3d10e3  12 677  34741.205
  287.7613-15.004 24.0  2428.453 25.0 -37169.280 6063a00f1  3d10f3  12 677  34740.828
  287.7650-14.899 20.0  2149.765 21.0 -36890.147 6063a00f1  3d10f3  12 677  34740.382
```
"""

import f311.filetypes as ft

f = ft.load_any_file("c2dabrookek.asc")

print(repr(f[0]).replace(", ", ",\n              "))

