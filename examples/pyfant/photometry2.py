"""
This program prints the calculated magnitude of Vega measured in different systems.

Values listed in system 'ab' should agree with table 'Vega 0 AB Magnitude Conversion' found in
http://www.astronomy.ohio-state.edu/~martini/usefuldata.html (they do)
"""
import f311.pyfant as pf

print(__doc__)

vega_sp = pf.get_vega_spectrum()

for system in ["stdflux", "vega", "ab"]:
    print("\nSystem: %s\n=============" % system)

    for name in "UBVRIJHK":
        print("%s: %g" % (name, pf.calculate_magnitude(vega_sp, name, system)["cmag"]))