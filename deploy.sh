#!/bin/bash
# (20230717)
# Updated deploy method to use twine
# Reference: https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/        
python setup.py sdist
twine check dist/*
twine upload dist/*
