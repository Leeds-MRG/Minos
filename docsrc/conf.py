# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
#sys.path.insert(0, os.path.abspath('../../../')) # adding root directory (for some reason).

# -- Project information -----------------------------------------------------

project = 'Minos'
copyright = '2022, Open MIT License'
author = 'Robert Clay, Luke Archer, Hugh Rice, and Nik Lomax'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['myst_parser',
              'sphinx.ext.autodoc',  # autodoc functionality for docs.
              'sphinx.ext.napoleon',  # convert numpy style docstrings to reST.
              'sphinx.ext.githubpages',  # Auto adds .nojekyll file to docs source.
              # If using make clean its deleted so auto add it back on compile.
              'sphinx.ext.viewcode',  # should allow "view source" buttons in api to work.
              'sphinxcontrib.bibtex',  # allows for references from a .bib biblatex file.
              'nbsphinx',  # notebooks in sphinx.
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to minos directory, that match files and
# directories to ignore when looking for minos files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# see for more bibtext details.
# https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html
bibtex_bibfiles = ['refs.bib']

#
#nbsphinx_custom_formats = {
#    '.Rmd': ['jupytext.reads', {'fmt': 'Rmd'}],
#}
#nbsphinx_kernel_name = 'IRkernel'

##############################################################################
# -- Options for HTML output -------------------------------------------------
##############################################################################
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_show_sourcelink = False

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']