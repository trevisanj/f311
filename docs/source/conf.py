#!/usr/bin/env python
# -*- coding: utf-8 -*-

#*#*#*#
# -JT- Made changes to increase the maximum width of the reading area
# -JT- http://stackoverflow.com/questions/23211695/modifying-content-width-of-the-sphinx-theme-read-the-docs
# -JT- Files _templates/layout.html and _static/style.css are part of this solution
#*#*#*#

#
# F311 documentation build configuration file, created by
# sphinx-quickstart on Wed Dec 21 16:20:55 2016.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

from recommonmark.parser import CommonMarkParser


extensions = ['sphinx.ext.todo', 'sphinx.ext.autodoc', 'sphinx.ext.napoleon']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']


# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_parsers = {'.md': CommonMarkParser}


source_suffix = ['.rst', '.md']

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'F311'
copyright = '2015-2017, JT'
author = 'JT'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '17.9.27.0'
# The full version, including alpha/beta/rc tags.
release = '17.9.27.0'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["hapi.rst"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

# html_theme = 'alabaster'
# html_theme = 'sphinxdoc'
# html_theme = 'haiku'
# html_theme = 'graphite'
# html_theme_path = ["/home/j/Documents/projects/astro/github/f311/docs"]


# import sphinx_readable_theme
# html_theme_path = [sphinx_readable_theme.get_html_theme_path()]
# html_theme = 'readable'

import sphinx_rtd_theme
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}
html_theme_options = {"logo_only": True}



# [theme]
# inherit = basic
# stylesheet = css/theme.css
#
# [options]
# typekit_id = hiw1hhg
# analytics_id =
# sticky_navigation = False
# logo_only =
# collapse_navigation = False
# display_version = True
# navigation_depth = 4
# prev_next_buttons_location = bottom
# canonical_url =




# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'f311doc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    'papersize': 'a4paper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    'preamble': r'''
\usepackage{charter}
\usepackage[defaultsans]{lato}
\usepackage{inconsolata}
''',


    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# # https://tex.stackexchange.com/questions/20182/how-to-use-unicode-characters-with-sphinx-rst-documents-and-properly-generate-pd
# latex_elements = {
#     'inputenc': '',
#     'utf8extra': '',
#     'preamble': '''
# \usepackage{fontspec}
# \setsansfont{Arial}
# \setromanfont{Arial}
# \setmonofont[12pt]{DejaVu Sans Mono}
# ''',
# }

# latex_elements = {
#     'preamble': '''
# % Enable unicode and use Courier New to ensure the card suit
# % characters that are part of the 'random' module examples
# % appear properly in the PDF output.
# \\usepackage{fontspec}
# \\setmonofont{Courier New}
# ''',
#     # disable font inclusion
#     'fontpkg': '',
#     'fontenc': '',
#     # Fix Unicode handling by disabling the defaults for a few items
#     # set by sphinx
#     'inputenc': '',
#     'utf8extra': '',
# }

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'f311.tex', 'F311 Documentation',
     'Julio Trevisan', 'manual'),
]




# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'f311', 'f311Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'f311', 'F311 Documentation',
     author, 'f311', 'One line description of project.',
     'Miscellaneous'),
]


numfig = True
numfig_format = {'figure': 'Figure %s',
                 'table': 'Table %s',
                 'code-block': 'Listing %s',
                 'section': 'Section %s'
                 }

def setup(app):
    app.add_stylesheet('custom.css')