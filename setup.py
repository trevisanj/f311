import sys
import os

if sys.version_info[0] < 3:
    print("Python version detected:\n*****\n{0!s}\n*****\nCannot run, must be using Python 3".format(sys.version))
    sys.exit()

from setuptools import setup, find_packages
from glob import glob


def find_scripts(pkgnames):
    ret = []
    for pkgname in pkgnames:
        for item in os.walk(pkgname):
            _, last = os.path.split(item[0])
            if last == "scripts":
                ret.extend(glob(os.path.join(item[0], '*.py')))
    return ret


pkgs = find_packages()
scripts = find_scripts(["f311"])


setup(
    name='f311',
    packages=find_packages(),
    include_package_data=True,
    version='0.17.7.18',
    license='GNU GPLv3',
    platforms='any',
    description='Collection of Astronomy-related libraries and applications in Python',
    author='Julio Trevisan',
    author_email='juliotrevisan@gmail.com',
    url='https://github.com/trevisanj/f311', # use the URL to the github repo
    keywords= ['astronomy', "fits", "spectroscopy", "spectral synthesis", "photometry",
               "honl-london", "nist", "hitran", "multiplicity"],
    install_requires=["a99>=0.17.7.17"],
    scripts=scripts
)


# TODO later install_requires=['numpy', 'matplotlib', 'pyqt5'],  # matplotlib never gets installed correctly by pip, but anyway...
