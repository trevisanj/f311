import sys
if sys.version_info[0] < 3:
    print("Python version detected:\n*****\n{0!s}\n*****\nCannot run, must be using Python 3".format(sys.version))
    sys.exit()

from setuptools import setup, find_packages
from glob import glob

setup(
    name = 'my_package',
    packages = find_packages(),
    include_package_data=True,
    version = '2000-b.c.',
    license = 'GNU GPLv3',
    platforms = 'any',
    description = 'Hyperdrive module for interstellar travel',
    author = 'João da Silva',
    author_email = 'your@email.here',
    url = 'http://github.com/your-github-user-name/my_package', # use the URL to the github repo
    keywords= ['your', 'keywords', 'here'],
    install_requires = ['f311'],
    scripts = glob('scripts/*.py')  # Considers system scripts all .py files in 'scripts' directory
)
