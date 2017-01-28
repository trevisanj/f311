#!/bin/bash

# This command creates the .rst files that are necessary for Sphinx to compile the docstrings from my module

sphinx-apidoc -f -o source/autodoc ../f311
