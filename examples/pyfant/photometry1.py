import f311.pyfant as pf
import matplotlib.pyplot as plt
import numpy as np

BAND_NAME = "B"
STYLE = {"color": (0, 0, 0), "lw": 2}
sp = pf.get_vega_spectrum()

bp = pf.UBVTabulated(BAND_NAME)
filtered = sp*bp
x_band = sp.x[np.logical_and(sp.x >= bp.l0, sp.x <= bp.lf)]

ax = plt.subplot(311)
plt.plot(sp.x, sp.y, **STYLE)
plt.title("Source Spectrum (Vega)")

plt.subplot(312, sharex=ax)
plt.plot(x_band, bp.ufunc()(x_band), **STYLE)
plt.ylim([0, 1.05])
plt.title("Bandpass Filter (%s)" % BAND_NAME)

plt.subplot(313, sharex=ax)
plt.plot(filtered.x, filtered.y, **STYLE)
plt.title("Filtered Spectrum")
plt.xlabel("Wavelength ($\AA$)")

ax.set_xlim([bp.l0-100, bp.lf+100])
plt.tight_layout()
plt.show()
