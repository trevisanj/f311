"""Plots ESO sky model"""
from astropy.io import fits
import matplotlib.pyplot as plt


def load_eso_sky(filename):
    """Loads ESO sky model and returns (lambda, emission, transmission)"""

    hl = fits.open("eso-sky.fits")
    d = hl[1].data

    return d["lam"]*10000, d["flux"], d["trans"]


# lam:     vacuum wavelength in micron
# flux:    sky emission radiance flux in ph/s/m2/micron/arcsec2
# dflux1:  sky emission -1sigma flux uncertainty
# dflux2:  sky emission +1sigma flux uncertainty
# dtrans:  sky transmission
# dtrans1: sky transmission -1sigma uncertainty
# dtrans2: sky transmission +1sigma uncertainty


hl = fits.open("eso-sky.fits")
d = hl[1].data

x, em, tr = load_eso_sky("eso-sky.fits")
ax = plt.subplot(211)
plt.plot(x, em, "k")
plt.title("Emission")

plt.subplot(212, sharex=ax)
plt.plot(x, tr, "k")
plt.title("Transmission")
plt.xlabel("Wavelength ($\AA$)")
plt.xlim(x[[0, -1]])


plt.tight_layout()
plt.show()




# # Version 1
# # dflux1, dflux2, dtrans1, dtrans2 didn't seem to be that useful
# hl = fits.open("eso-sky.fits")
# d = hl[1].data
#
# x = d["lam"]
#
# plt.subplot(211)
# plt.plot(x, d["flux"], "k", lw=2)
# plt.plot(x, d["dflux1"], "k--")
# plt.plot(x, d["dflux2"], "k--")
#
# plt.subplot(212)
# plt.plot(x, d["trans"], "k", lw=2)
# plt.plot(x, d["dtrans1"], "k--")
# plt.plot(x, d["dtrans2"], "k--")
#
# plt.show()

# # Version 0
# names = [column.name for column in d.columns]
# nc = len(names)
#
# x = d[names[0]]
#
# for name in names[1:]:
#     y = d[name]
#     plt.plot(x, y)
#
# plt.show()