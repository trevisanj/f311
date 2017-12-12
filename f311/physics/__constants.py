# TODO wanna get rid of this

__all__ = ["symbols", "SYMBOLS", "C", "H"]


# All values in CGS
class LightSpeed(float):
    """Light speed in cm/s (CGS) units"""

class Planck(float):
    """Planck's constant in cm**2*g/s"""

#: Light speed in cm/s
C = LightSpeed(299792458. * 100)
#: Planck's constant in cm**2*g/s
H = Planck(6.6261e-27)

